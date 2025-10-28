# backend/app/controller/client_controller.py

from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
# Importa los servicios necesarios
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..services.alerts_service import AlertsService
from ..services.devices_service import DevicesService
# Importa los schemas de respuesta
from ..model.dto.response_schemas import PatientResponse, ReadingResponse, AlertResponse, DeviceResponse # Asume que existen
# Importa helper de parseo de fechas si lo moviste a utils
# from ..utils.datetime_helpers import parse_iso_datetime

# --- Define el Blueprint ---
# Puedes añadir un prefijo /me aquí si todas las rutas lo usan, o mantenerlo individualmente
client_bp = Blueprint("client", __name__)

# --- Instancias de servicios ---
_patients_service = PatientsService()
_metrics_service = MetricsService()
_alerts_service = AlertsService()
_devices_service = DevicesService()

# --- Instancias de Schemas ---
_patient_out = PatientResponse() # Para perfil individual
_readings_out_many = ReadingResponse(many=True)
_alert_out_many = AlertResponse(many=True)
_device_out_many = DeviceResponse(many=True) # Para listar dispositivos

# === Helper para obtener Patient ID del User ID (requiere método en servicio) ===
def _get_patient_id_from_jwt() -> int:
    """Obtiene el user_id del JWT y busca el patient_id asociado."""
    user_id = get_jwt_identity()
    # Necesitas implementar esta búsqueda en PatientsService/Repository
    # patient = _patients_service.get_by_user_id(user_id)
    # if not patient:
    #     abort(404, description="Perfil de paciente no encontrado para este usuario.")
    # return patient.id
    # --- Placeholder ---
    print(f"TODO: Implementar _patients_service.get_by_user_id({user_id})")
    # Asume que user_id 1 corresponde a patient_id 1 para demo
    if user_id == 1: # ¡Quita esta lógica hardcoded!
         return 1
    abort(404, description="Perfil de paciente no encontrado (Placeholder check).")
    # --- Fin Placeholder ---


# === Rutas para el Cliente ===

@client_bp.get("/me/profile")
@jwt_required()
def get_my_profile():
    """Obtiene el perfil del paciente asociado al usuario autenticado."""
    user_id = get_jwt_identity()
    # Necesitas un método en PatientsService/Repository para buscar por user_id
    # patient = _patients_service.get_by_user_id(user_id)
    # if not patient:
    #     abort(404, description="Perfil de paciente no encontrado para este usuario.")
    # return _patient_out.dump(patient), 200
    # --- Placeholder ---
    print(f"TODO: Implementar PatientsService.get_by_user_id({user_id})")
    patient_id = _get_patient_id_from_jwt() # Usa el helper
    # Simula respuesta usando datos básicos
    return {"id": patient_id, "user_id": user_id, "full_name": "Usuario Demo", "email": "usuario@demo.com"}, 200
    # --- Fin Placeholder ---

@client_bp.get("/me/devices")
@jwt_required()
def get_my_devices():
    """Lista los dispositivos asignados al paciente autenticado."""
    patient_id = _get_patient_id_from_jwt() # Obtiene el ID del paciente asociado al token
    devices = _devices_service.list_by_patient(patient_id)
    return {"items": _device_out_many.dump(devices)}, 200

@client_bp.get("/me/readings/latest") # Endpoint específico para el dashboard
@jwt_required()
def get_my_latest_readings():
    """Obtiene la última lectura registrada para el dashboard."""
    patient_id = _get_patient_id_from_jwt()
    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        # No tiene dispositivos, devuelve vacío o un error apropiado
        return {"latest_reading": None, "device_status": "No asignado"}, 200 # O 404

    # Asume el primer dispositivo por ahora (o el marcado como 'active')
    # Podrías necesitar lógica para manejar múltiples dispositivos
    device = devices[0]

    # Necesitas un método en MetricsService/Repository para obtener solo la última lectura
    # latest = _metrics_service.get_latest_reading(device.id)
    # --- Placeholder ---
    print(f"TODO: Implementar MetricsService.get_latest_reading({device.id})")
    # Simula una lectura reciente
    from datetime import datetime, timezone
    latest = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "heart_rate_bpm": 75,
        "spo2_pct": 98,
        "temp_c": "36.5" # Asegúrate que el schema maneje string/decimal
    }
    # --- Fin Placeholder ---

    # El schema individual (no 'many')
    latest_dump = ReadingResponse().dump(latest) if latest else None

    # Combina con el estado del dispositivo
    return {
        "latest_reading": latest_dump,
        "device_status": device.status # O información de batería si la obtienes
        }, 200

@client_bp.get("/me/readings") # Historial
@jwt_required()
def get_my_readings_history():
    """Obtiene el historial de lecturas para el usuario autenticado, con filtros."""
    patient_id = _get_patient_id_from_jwt()
    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        return {"items": []}, 200 # No tiene dispositivos

    # Asume el primer dispositivo activo
    device_id = devices[0].id # TODO: Mejorar selección si hay múltiples dispositivos

    # Obtener parámetros de query para filtrar por fecha
    dt_from_str = request.args.get("from")
    dt_to_str = request.args.get("to")
    limit = request.args.get("limit", default=1000, type=int)

    # Usa tu helper de parseo de fechas (asume que está en utils o aquí)
    # dt_from = parse_iso_datetime(dt_from_str)
    # dt_to = parse_iso_datetime(dt_to_str)
    # --- Placeholder de parseo ---
    from ..controller.telemetry_controller import _parse_dt # Reusa el de telemetry temporalmente
    dt_from = _parse_dt(dt_from_str)
    dt_to = _parse_dt(dt_to_str)
    # --- Fin Placeholder ---

    readings = _metrics_service.list_range(device_id, dt_from, dt_to, limit)
    return {"items": _readings_out_many.dump(readings)}, 200

@client_bp.get("/me/alerts")
@jwt_required()
def get_my_alerts():
    """Lista las alertas para el paciente autenticado."""
    patient_id = _get_patient_id_from_jwt()
    limit = request.args.get("limit", default=50, type=int)
    # Podrías añadir filtros (ej. ?acknowledged=false)
    alerts = _alerts_service.list_alerts_for_patient(patient_id, limit=limit)
    return {"items": _alert_out_many.dump(alerts)}, 200

# --- Rutas Antiguas (Revisar si mantenerlas) ---
# /patients podría moverse a admin si no es para clientes.
# /readings/<id>/last24h y /metrics/<id>/last24h podrían reemplazarse por /me/readings/latest o /me/readings?limit=X&hours=24

# @client_bp.get("/patients") ... (evaluar si quitar o mover)
# @client_bp.get("/readings/<int:device_id>/last24h") ... (evaluar si quitar)
# @client_bp.get("/metrics/<int:device_id>/last24h") ... (evaluar si quitar)