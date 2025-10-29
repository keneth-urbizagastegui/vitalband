from flask import Blueprint, request, abort
# IMPORTANTE: Asegúrate que jwt_required se importa correctamente
from flask_jwt_extended import jwt_required, current_user
from ..model.models import User
# Importa los servicios necesarios
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..services.alerts_service import AlertsService
from ..services.devices_service import DevicesService
# Importa los schemas de respuesta
from ..model.dto.response_schemas import PatientResponse, ReadingResponse, AlertResponse, DeviceResponse
# Importa el helper de parseo de fechas si lo moviste
from ..controller.telemetry_controller import _parse_dt # Asumiendo que está ahí

# --- Define el Blueprint ---
client_bp = Blueprint("client", __name__)

# --- Instancias de servicios ---
_patients_service = PatientsService()
_metrics_service = MetricsService()
_alerts_service = AlertsService()
_devices_service = DevicesService()

# --- Instancias de Schemas ---
_patient_out = PatientResponse()
_readings_out_many = ReadingResponse(many=True)
_alert_out_many = AlertResponse(many=True)
_device_out_many = DeviceResponse(many=True)

# === Helper REESCRITO para usar current_user ===
def _get_patient_from_jwt() -> dict:
    """
    Obtiene el usuario actual (cargado por el user_loader)
    y devuelve un dict de paciente simulado o real.
    """
    user: User = current_user

    if not user:
        abort(401, description="Usuario no encontrado para este token.")

    # --- Lógica REAL (reemplaza placeholder si tienes PatientsService.get_by_user_id) ---
    # Intenta obtener el paciente real asociado al user_id del token
    patient = _patients_service.get_by_user_id(user.id) # Usa el método del servicio
    if not patient:
         # Si no se encuentra un paciente asociado, lanzar error
         abort(404, description=f"Perfil de paciente no encontrado para el usuario {user.email} (ID: {user.id}).")

    # Devuelve un diccionario simple con la información necesaria
    return {"id": patient.id, "user_id": user.id, "email": user.email}
    # --- Fin Lógica REAL ---

# === Rutas para el Cliente (Actualizadas) ===

@client_bp.get("/me/profile")
# --- REVERTIDO ---
@jwt_required()
# --- FIN REVERSIÓN ---
def get_my_profile():
    """Obtiene el perfil del paciente asociado al usuario autenticado."""
    patient_data = _get_patient_from_jwt()
    patient_id = patient_data["id"]

    # --- Lógica Real ---
    patient = _patients_service.get(patient_id)
    if not patient:
        # Esto no debería pasar si _get_patient_from_jwt funcionó, pero por seguridad
        abort(404, description="Detalle del perfil de paciente no encontrado.")
    return _patient_out.dump(patient), 200
    # --- Fin Lógica Real ---

@client_bp.get("/me/devices")
# --- REVERTIDO ---
@jwt_required()
# --- FIN REVERSIÓN ---
def get_my_devices():
    """Lista los dispositivos asignados al paciente autenticado."""
    patient_data = _get_patient_from_jwt()
    patient_id = patient_data["id"]

    devices = _devices_service.list_by_patient(patient_id)
    return {"items": _device_out_many.dump(devices)}, 200

@client_bp.get("/me/readings/latest")
# --- REVERTIDO ---
@jwt_required()
# --- FIN REVERSIÓN ---
def get_my_latest_readings():
    """Obtiene la última lectura registrada para el dashboard."""
    patient_data = _get_patient_from_jwt()
    patient_id = patient_data["id"]

    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        return {"latest_reading": None, "device_status": "No asignado"}, 200

    # Asume que el cliente solo tiene un dispositivo activo a la vez
    # Podrías necesitar lógica más compleja si puede tener varios
    device = devices[0]

    # --- Lógica Real ---
    latest_reading = _metrics_service.get_latest_reading(device.id) # Usa el método del servicio
    # --- Fin Lógica Real ---

    latest_dump = ReadingResponse().dump(latest_reading) if latest_reading else None

    return {
        "latest_reading": latest_dump,
        "device_status": device.status # Estado del dispositivo encontrado
        }, 200

@client_bp.get("/me/readings") # Historial
# --- REVERTIDO ---
@jwt_required()
# --- FIN REVERSIÓN ---
def get_my_readings_history():
    """Obtiene el historial de lecturas para el usuario autenticado, con filtros."""
    patient_data = _get_patient_from_jwt()
    patient_id = patient_data["id"]

    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        return {"items": []}, 200

    device_id = devices[0].id

    # Parseo de parámetros de fecha y límite (sin cambios)
    dt_from_str = request.args.get("from")
    dt_to_str = request.args.get("to")
    limit = request.args.get("limit", default=1000, type=int)

    dt_from = _parse_dt(dt_from_str)
    dt_to = _parse_dt(dt_to_str)

    readings = _metrics_service.list_range(device_id, dt_from, dt_to, limit)
    return {"items": _readings_out_many.dump(readings)}, 200

@client_bp.get("/me/alerts")
# --- REVERTIDO ---
@jwt_required()
# --- FIN REVERSIÓN ---
def get_my_alerts():
    """Lista las alertas para el paciente autenticado."""
    patient_data = _get_patient_from_jwt()
    patient_id = patient_data["id"]

    limit = request.args.get("limit", default=50, type=int)
    # Podrías añadir filtro 'acknowledged' aquí si lo necesitas
    # acknowledged_param = request.args.get("acknowledged")
    # acknowledged = None if acknowledged_param is None else acknowledged_param.lower() == 'false'
    alerts = _alerts_service.list_alerts_for_patient(patient_id, limit=limit) # Añade acknowledged si lo usas
    return {"items": _alert_out_many.dump(alerts)}, 200