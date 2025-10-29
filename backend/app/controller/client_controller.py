from flask import Blueprint, request, abort
from flask_jwt_extended import jwt_required, current_user # <-- CAMBIADO
from ..model.models import User # <-- AÑADIDO
# Importa los servicios necesarios
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..services.alerts_service import AlertsService
from ..services.devices_service import DevicesService
# Importa los schemas de respuesta
from ..model.dto.response_schemas import PatientResponse, ReadingResponse, AlertResponse, DeviceResponse 

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
    y devuelve un dict de paciente simulado.
    """
    user: User = current_user # Esto es inyectado por el @jwt.user_lookup_loader
    
    if not user:
        # Si el loader falló, current_user será None.
        abort(401, description="Usuario no encontrado para este token.")
    
    # --- Lógica de Placeholder CORREGIDA ---
    # El log del backend mostró que el user_id era 2.
    # Tu placeholder anterior solo manejaba user_id 1.
    
    if user.id == 1: # admin@demo.com (asumido)
        # Simula un objeto Paciente
        return {"id": 1, "user_id": 1} # Devuelve un dict
    if user.id == 2: # client@demo.com (el de tu log)
        # Simula un objeto Paciente
        return {"id": 2, "user_id": 2} # Devuelve un dict
        
    abort(404, description=f"Perfil de paciente no encontrado (Placeholder no maneja user_id {user.id}).")
    # --- Fin Placeholder ---


# === Rutas para el Cliente (Actualizadas) ===

@client_bp.get("/me/profile")
@jwt_required()
def get_my_profile():
    """Obtiene el perfil del paciente asociado al usuario autenticado."""
    patient_data = _get_patient_from_jwt() # Llama al helper
    
    # --- Placeholder ---
    # El helper ya devuelve un dict simulado, solo lo completamos
    patient_data["full_name"] = "Usuario Demo (Placeholder)"
    patient_data["email"] = current_user.email
    return patient_data, 200
    # --- Fin Placeholder ---

@client_bp.get("/me/devices")
@jwt_required()
def get_my_devices():
    """Lista los dispositivos asignados al paciente autenticado."""
    patient_data = _get_patient_from_jwt() # Llama al helper
    patient_id = patient_data["id"] # Obtiene el ID del dict
    
    devices = _devices_service.list_by_patient(patient_id)
    return {"items": _device_out_many.dump(devices)}, 200

@client_bp.get("/me/readings/latest") # Endpoint que fallaba
@jwt_required()
def get_my_latest_readings():
    """Obtiene la última lectura registrada para el dashboard."""
    patient_data = _get_patient_from_jwt() # Llama al helper
    patient_id = patient_data["id"] # Obtiene el ID del dict

    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        return {"latest_reading": None, "device_status": "No asignado"}, 200 

    device = devices[0]

    # --- Placeholder (como en tu código original, pero añadiendo IDs) ---
    print(f"TODO: Implementar MetricsService.get_latest_reading({device.id})")
    from datetime import datetime, timezone
    latest = {
        "id": 1234, # ID de lectura simulado
        "device_id": device.id, # ID de dispositivo
        "ts": datetime.now(timezone.utc).isoformat(),
        "heart_rate_bpm": 75,
        "spo2_pct": 98,
        "temp_c": "36.5" 
    }
    # --- Fin Placeholder ---

    latest_dump = ReadingResponse().dump(latest) if latest else None

    return {
        "latest_reading": latest_dump,
        "device_status": device.status 
        }, 200

@client_bp.get("/me/readings") # Historial
@jwt_required()
def get_my_readings_history():
    """Obtiene el historial de lecturas para el usuario autenticado, con filtros."""
    patient_data = _get_patient_from_jwt() # Llama al helper
    patient_id = patient_data["id"] # Obtiene el ID del dict
    
    devices = _devices_service.list_by_patient(patient_id)
    if not devices:
        return {"items": []}, 200 

    device_id = devices[0].id 

    dt_from_str = request.args.get("from")
    dt_to_str = request.args.get("to")
    limit = request.args.get("limit", default=1000, type=int)

    # --- Placeholder de parseo (como en tu original) ---
    from ..controller.telemetry_controller import _parse_dt 
    dt_from = _parse_dt(dt_from_str)
    dt_to = _parse_dt(dt_to_str)
    # --- Fin Placeholder ---

    readings = _metrics_service.list_range(device_id, dt_from, dt_to, limit)
    return {"items": _readings_out_many.dump(readings)}, 200

@client_bp.get("/me/alerts")
@jwt_required()
def get_my_alerts():
    """Lista las alertas para el paciente autenticado."""
    patient_data = _get_patient_from_jwt() # Llama al helper
    patient_id = patient_data["id"] # Obtiene el ID del dict
    
    limit = request.args.get("limit", default=50, type=int)
    alerts = _alerts_service.list_alerts_for_patient(patient_id, limit=limit)
    return {"items": _alert_out_many.dump(alerts)}, 200