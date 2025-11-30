# backend/app/controller/telemetry_controller.py

from datetime import datetime, timezone
from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from ..services.telemetry_service import TelemetryService
from ..services.devices_service import DevicesService # Para verificar pertenencia
from ..services.patients_service import PatientsService # Para verificar pertenencia

from ..model.dto.request_schemas import DeviceTelemetryRequest
from ..model.dto.response_schemas import DeviceTelemetryResponse
# Importa helper de parseo de fechas si lo moviste a utils
# from ..utils.datetime_helpers import parse_iso_datetime

telemetry_bp = Blueprint("telemetry", __name__)
_service = TelemetryService()
_devices_service = DevicesService()
_patients_service = PatientsService()
_in = DeviceTelemetryRequest()
_out = DeviceTelemetryResponse()
_out_many = DeviceTelemetryResponse(many=True)

# Helper para parsear fechas ISO (reutilizado)
def _parse_dt(s: str | None) -> datetime | None:
    # ... (misma implementación robusta que antes) ...
    if not s: return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        abort(400, description=f"Formato de fecha inválido: '{s}'.")


# === Helper para verificar permisos de acceso a telemetría ===
def _check_telemetry_permission(device_id: int, required_level: str = "read"):
    """Verifica si el usuario/token actual tiene permiso para acceder a la telemetría."""
    user_id_str = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role")

    if role == "admin":
        return

    if role == "client":
        if required_level == "write":
            abort(403, description="Clientes no pueden escribir telemetría.")

        try:
            user_id = int(user_id_str) if isinstance(user_id_str, str) else user_id_str
        except Exception:
            abort(401, description="Identidad de token inválida.")

        patient = _patients_service.get_by_user_id(user_id)
        if not patient:
            abort(404, description="Perfil no encontrado.")

        device = _devices_service.get_patient_device(patient.id, device_id)
        if not device:
            abort(403, description="Acceso denegado a la telemetría de este dispositivo.")
        return

    if required_level == "write":
        abort(403, description="Permiso de escritura de telemetría no definido para este token.")
    abort(403, description="Acceso denegado.")


# --- Rutas ---

@telemetry_bp.post("/devices/<int:device_id>/telemetry")
@jwt_required() # Requiere algún token válido
def create_telemetry(device_id: int):
    """Recibe y guarda un nuevo registro de telemetría."""
    _check_telemetry_permission(device_id, required_level="write") # Verifica permiso

    try:
        payload = _in.load(request.get_json(force=True) or {})
    except ValidationError as err:
        return {"messages": err.messages}, 400

    try:
        tel = _service.create(device_id, payload)
        return _out.dump(tel), 201
    except Exception as e:
        # Loggear error 'e'
        if hasattr(e, 'code') and e.code == 404: abort(404, "Dispositivo no encontrado.")
        abort(500, description="Error al guardar la telemetría.")


@telemetry_bp.get("/devices/<int:device_id>/telemetry")
@jwt_required()
def list_telemetry(device_id: int):
    """Lista los registros de telemetría para un dispositivo."""
    _check_telemetry_permission(device_id, required_level="read") # Verifica permiso

    dt_from = _parse_dt(request.args.get("from"))
    dt_to = _parse_dt(request.args.get("to"))
    limit = request.args.get("limit", default=500, type=int)

    try:
        items = _service.list_by_device(device_id, dt_from, dt_to, limit)
        return {"items": _out_many.dump(items)}, 200
    except Exception as e:
        if hasattr(e, 'code') and e.code == 404: abort(404, "Dispositivo no encontrado.")
        # Loggear error 'e'
        abort(500, description="Error al obtener la telemetría.")
