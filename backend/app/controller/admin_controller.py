# backend/app/controller/admin_controller.py

from functools import wraps
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError

# --- Servicios ---
from ..services.patients_service import PatientsService
from ..services.devices_service import DevicesService
from ..services.alerts_service import AlertsService
from ..services.thresholds_service import ThresholdsService
# (Importa User service si necesitas gestionar usuarios admin/cliente)
# from ..services.users_service import UsersService

# --- Schemas (DTOs) ---
from ..model.dto.request_schemas import (
    PatientCreateRequest, PatientUpdateRequest,
    DeviceCreateRequest, DeviceUpdateRequest, DeviceAssignRequest, # Asume que existen
    ThresholdUpdateRequest, AlertAcknowledgeRequest # Asume que existen
)
from ..model.dto.response_schemas import (
    PatientResponse, DeviceResponse, AlertResponse, ThresholdResponse # Asume que existen
)

admin_bp = Blueprint("admin", __name__) # Prefijo manejado en app/__init__.py

# --- Instancias de Servicios ---
_patients_service = PatientsService()
_devices_service = DevicesService()
_alerts_service = AlertsService()
_thresholds_service = ThresholdsService()
# _users_service = UsersService() # Si gestionas usuarios

# --- Instancias de Schemas ---
_patient_create_in = PatientCreateRequest()
_patient_update_in = PatientUpdateRequest()
_patient_out = PatientResponse()
_patient_out_many = PatientResponse(many=True)

_device_create_in = DeviceCreateRequest() # Asume existencia
_device_update_in = DeviceUpdateRequest() # Asume existencia
_device_assign_in = DeviceAssignRequest() # Asume existencia
_device_out = DeviceResponse() # Asume existencia
_device_out_many = DeviceResponse(many=True) # Asume existencia

_alert_ack_in = AlertAcknowledgeRequest() # Asume existencia
_alert_out = AlertResponse() # Asume existencia
_alert_out_many = AlertResponse(many=True) # Asume existencia

_threshold_update_in = ThresholdUpdateRequest() # Asume existencia
_threshold_out = ThresholdResponse() # Asume existencia
_threshold_out_many = ThresholdResponse(many=True) # Asume existencia

# === Decorador para verificar rol de Admin ===
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required() # Primero verifica que haya un token válido
        def decorator(*args, **kwargs):
            claims = get_jwt()
            # Asume que el rol está en los claims adicionales como 'role'
            if claims.get("role") != "admin":
                # 403 Forbidden si el rol no es admin
                abort(403, description="Acceso denegado: Se requiere rol de administrador.")
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# ===========================
# PACIENTES (CRUD Completo)
# ===========================

@admin_bp.post("/patients")
@admin_required()
def create_patient():
    """Crea un nuevo paciente."""
    payload = request.get_json() or {}
    try:
        data = _patient_create_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # CONSIDERACIÓN: Aquí asume que el user_id ya existe o se maneja en el servicio.
    # Podrías necesitar lógica adicional para crear el User si no se provee user_id.
    try:
        p = _patients_service.create_patient(**data)
        return _patient_out.dump(p), 201
    except Exception as e: # Captura errores potenciales (ej. email duplicado)
        # Loggear el error 'e' sería ideal aquí
        abort(409, description=f"No se pudo crear el paciente. ¿Email duplicado? ({e})")

@admin_bp.get("/patients")
@admin_required()
def list_patients_admin():
    """Lista todos los pacientes (potencialmente con filtros/paginación)."""
    # TODO: Añadir filtros (por nombre, email?) y paginación si es necesario
    patients = _patients_service.list_patients()
    return {"items": _patient_out_many.dump(patients)}, 200

@admin_bp.get("/patients/<int:patient_id>")
@admin_required()
def get_patient_detail(patient_id: int):
    """Obtiene los detalles de un paciente específico."""
    patient = _patients_service.get(patient_id)
    if not patient:
        abort(404, description="Paciente no encontrado.")
    return _patient_out.dump(patient), 200

@admin_bp.put("/patients/<int:patient_id>") # O usa PATCH
@admin_required()
def update_patient(patient_id: int):
    """Actualiza la información de un paciente."""
    # (Verifica existencia primero)
    if not _patients_service.get(patient_id): 
        abort(404, description="Paciente no encontrado.")

    payload = request.get_json() or {}
    try:
        data = _patient_update_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    updated_patient = _patients_service.update(patient_id, data)
    if not updated_patient:
        abort(500, description="Error al actualizar el paciente.")
    
    return _patient_out.dump(updated_patient), 200
    # --- FIN DEL CÓDIGO REAL ---

@admin_bp.delete("/patients/<int:patient_id>")
@admin_required()
def delete_patient(patient_id: int):
    """Elimina un paciente."""
    if not _patients_service.get(patient_id):
        abort(404, description="Paciente no encontrado.")

    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    success = _patients_service.delete(patient_id)
    if not success:
        abort(500, description="Error al eliminar el paciente.")
    
    return "", 204 # Éxito (No Content)
    # --- FIN DEL CÓDIGO REAL ---

# ===========================
# DISPOSITIVOS (CRUD + Asignación)
# ===========================

@admin_bp.post("/devices")
@admin_required()
def register_device():
    """Registra un nuevo dispositivo en el sistema."""
    payload = request.get_json() or {}
    try:
        data = _device_create_in.load(payload) # Valida 'serial' y 'model'
    except ValidationError as err:
        return {"messages": err.messages}, 400

    try:
        # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
        device = _devices_service.create(**data)
        return _device_out.dump(device), 201
        # --- FIN DEL CÓDIGO REAL ---
    except ValueError as e: # Captura el error de serial duplicado del servicio
         abort(409, description=str(e))
    except Exception as e: 
        abort(500, description=f"Error interno al registrar dispositivo: {e}")

@admin_bp.get("/devices")
@admin_required()
def list_devices_admin():
    """Lista todos los dispositivos registrados."""
    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    # TODO: Añadir paginación si es necesario
    devices = _devices_service.list_all()
    return {"items": _device_out_many.dump(devices)}, 200
    # --- FIN DEL CÓDIGO REAL ---

@admin_bp.get("/devices/<int:device_id>")
@admin_required()
def get_device_detail(device_id: int):
    """Obtiene los detalles de un dispositivo específico."""
    device = _devices_service.get_by_id(device_id)
    if not device:
        abort(404, description="Dispositivo no encontrado.")
    return _device_out.dump(device), 200

@admin_bp.put("/devices/<int:device_id>") # O PATCH
@admin_required()
def update_device(device_id: int):
    """Actualiza información del dispositivo (ej. estado, modelo)."""
    device = _devices_service.get_by_id(device_id) # Se necesita el objeto
    if not device:
        abort(404, description="Dispositivo no encontrado.")

    payload = request.get_json() or {}
    try:
        data = _device_update_in.load(payload) # Valida los campos a actualizar (ej. status, model)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    updated_device = _devices_service.update(device, data)
    if not updated_device:
         abort(500, "Error al actualizar dispositivo.")
    return _device_out.dump(updated_device), 200
    # --- FIN DEL CÓDIGO REAL ---

@admin_bp.post("/devices/<int:device_id>/assign")
@admin_required()
def assign_device_to_patient(device_id: int):
    """Asigna o desasigna un dispositivo a un paciente."""
    payload = request.get_json() or {}
    try:
        data = _device_assign_in.load(payload) # Valida { "patient_id": int | null }
    except ValidationError as err:
        return {"messages": err.messages}, 400

    patient_id = data.get("patient_id") # Puede ser None

    # Verifica si el paciente existe si se va a asignar
    if patient_id is not None and not _patients_service.get(patient_id):
        abort(404, description=f"Paciente con ID {patient_id} no encontrado.")

    device = _devices_service.assign_to_patient(device_id, patient_id)
    if not device:
        abort(404, description="Dispositivo no encontrado.")

    return _device_out.dump(device), 200

@admin_bp.delete("/devices/<int:device_id>")
@admin_required()
def delete_device(device_id: int):
    """Elimina un dispositivo (¡cuidado con los datos asociados!)."""
    device = _devices_service.get_by_id(device_id) # Necesitamos el objeto
    if not device:
        abort(404, description="Dispositivo no encontrado.")

    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    success = _devices_service.delete(device)
    if not success:
        abort(500, description="Error al eliminar el dispositivo.")
    return "", 204
    # --- FIN DEL CÓDIGO REAL ---

# ===========================
# ALERTAS (Gestión)
# ===========================

@admin_bp.get("/patients/<int:patient_id>/alerts")
@admin_required()
def list_alerts_for_patient(patient_id: int):
    """Lista las alertas para un paciente específico."""
    if not _patients_service.get(patient_id):
        abort(404, description="Paciente no encontrado.")

    limit = request.args.get("limit", default=100, type=int)
    # Podrías añadir filtros por fecha, tipo, severidad, acknowledged status
    alerts = _alerts_service.list_alerts_for_patient(patient_id, limit=limit)
    return {"items": _alert_out_many.dump(alerts)}, 200

@admin_bp.get("/alerts/<int:alert_id>") # Ruta podría ser /admin/alerts/<id>
@admin_required()
def get_alert_detail(alert_id: int):
     """Obtiene detalle de una alerta específica."""
     alert = _alerts_service.get(alert_id)
     if not alert:
         abort(404, description="Alerta no encontrada.")
     return _alert_out.dump(alert), 200


@admin_bp.post("/alerts/<int:alert_id>/acknowledge")
@admin_required()
def acknowledge_alert(alert_id: int):
    """Marca una alerta como reconocida por el admin actual."""
    user_id_str = get_jwt_identity() # Obtiene el ID del admin (como string)
    user_id = int(user_id_str) # Convierte a int para el servicio

    payload = request.get_json() or {}
    try:
        data = _alert_ack_in.load(payload) 
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
    updated_alert = _alerts_service.acknowledge(
        alert_id, 
        user_id, 
        data.get("notes") # Pasa las notas (aunque el modelo actual no las use)
    )
    
    if not updated_alert:
        abort(404, description="Alerta no encontrada o ya reconocida.") 
    
    return _alert_out.dump(updated_alert), 200
    # --- FIN DEL CÓDIGO REAL ---

# ===========================
# UMBRALES (Thresholds)
# ===========================

@admin_bp.get("/thresholds/global")
@admin_required()
def get_global_thresholds():
    """Obtiene los umbrales globales para todas las métricas."""
    metrics = ["heart_rate", "temperature", "spo2"] # O obtén de Enum
    thresholds = [_thresholds_service.get_thresholds(patient_id=None, metric=m) for m in metrics]
    # Filtra los que no tengan min/max definidos si quieres solo los existentes
    # existing_thresholds = [t for t in thresholds if t.get('min') is not None or t.get('max') is not None]
    # Serializa usando el schema adecuado
    return {"items": _threshold_out_many.dump(thresholds)}, 200

@admin_bp.put("/thresholds/global/<string:metric>")
@admin_required()
def set_global_threshold(metric: str):
    """Establece (upsert) el umbral global para una métrica."""
    if metric not in ["heart_rate", "temperature", "spo2"]:
        abort(400, description="Métrica inválida.")

    payload = request.get_json() or {}
    try:
        # Valida { "min_value": float | null, "max_value": float | null }
        data = _threshold_update_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    threshold = _thresholds_service.upsert_thresholds(
        patient_id=None,
        metric=metric,
        min_value=data.get("min_value"),
        max_value=data.get("max_value")
    )
    return _threshold_out.dump(threshold), 200


@admin_bp.get("/patients/<int:patient_id>/thresholds")
@admin_required()
def get_patient_thresholds(patient_id: int):
    """Obtiene los umbrales específicos de un paciente (o globales si no hay)."""
    if not _patients_service.get(patient_id):
        abort(404, description="Paciente no encontrado.")

    metrics = ["heart_rate", "temperature", "spo2"]
    # El servicio ya debería manejar la lógica de fallback a global si no hay específico
    thresholds = [_thresholds_service.get_thresholds(patient_id=patient_id, metric=m) for m in metrics]
    # Serializa usando el schema adecuado
    return {"items": _threshold_out_many.dump(thresholds)}, 200

@admin_bp.put("/patients/<int:patient_id>/thresholds/<string:metric>")
@admin_required()
def set_patient_threshold(patient_id: int, metric: str):
    """Establece (upsert) el umbral específico para un paciente y métrica."""
    if not _patients_service.get(patient_id):
        abort(404, description="Paciente no encontrado.")
    if metric not in ["heart_rate", "temperature", "spo2"]:
        abort(400, description="Métrica inválida.")

    payload = request.get_json() or {}
    try:
        data = _threshold_update_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    threshold = _thresholds_service.upsert_thresholds(
        patient_id=patient_id,
        metric=metric,
        min_value=data.get("min_value"),
        max_value=data.get("max_value")
    )
    return _threshold_out.dump(threshold), 200

# ===========================
# ALERTAS (Gestión Global)
# ===========================

@admin_bp.get("/alerts/pending")
@admin_required()
def get_pending_alerts():
    """Obtiene una lista de todas las alertas pendientes (no reconocidas) del sistema."""
    limit = request.args.get("limit", default=20, type=int)
    
    # Llama al nuevo método del servicio
    alerts = _alerts_service.list_pending_alerts(limit=limit)
    
    return {"items": _alert_out_many.dump(alerts)}, 200

# ===========================
# ESTADÍSTICAS (Opcional)
# ===========================

# @admin_bp.get("/stats")
# @admin_required()
# def get_admin_dashboard_stats():
#     """ Devuelve KPIs para el panel de admin. """
#     # Aquí iría la lógica para calcular:
#     # - Número de pacientes activos
#     # - Número de dispositivos conectados
#     # - Conteo de alertas recientes por tipo/severidad
#     # Necesitarías métodos en los servicios/repositorios para obtener estos datos agregados.
#     stats = {
#         "active_patients": _patients_service.count_active(), # Ejemplo
#         "active_devices": _devices_service.count_active(), # Ejemplo
#         "recent_alerts": _alerts_service.count_recent_by_severity() # Ejemplo
#     }
#     return jsonify(stats), 200