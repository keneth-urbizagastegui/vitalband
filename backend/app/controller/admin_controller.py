# backend/app/controller/admin_controller.py

from functools import wraps
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt
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

admin_bp = Blueprint("admin", __name__, url_prefix="/admin") # Prefijo /admin ya aquí

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
    if not _patients_service.get(patient_id): # Verifica existencia primero
        abort(404, description="Paciente no encontrado.")

    payload = request.get_json() or {}
    try:
        data = _patient_update_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # Necesitas un método update en PatientsService/Repository
    # Ejemplo: updated_patient = _patients_service.update(patient_id, data)
    # if not updated_patient:
    #     abort(500, description="Error al actualizar el paciente.")
    # return _patient_out.dump(updated_patient), 200
    # --- Placeholder ---
    print(f"TODO: Implementar PatientsService.update({patient_id}, {data})")
    # Simulación temporal de lectura post-actualización (no guarda nada)
    updated_patient = _patients_service.get(patient_id)
    # Sobrescribe campos localmente para la respuesta (simulación)
    if updated_patient:
        for key, value in data.items():
            if hasattr(updated_patient, key):
                setattr(updated_patient, key, value)
    return _patient_out.dump(updated_patient), 200
    # --- Fin Placeholder ---


@admin_bp.delete("/patients/<int:patient_id>")
@admin_required()
def delete_patient(patient_id: int):
    """Elimina un paciente."""
    if not _patients_service.get(patient_id):
        abort(404, description="Paciente no encontrado.")

    # Necesitas un método delete en PatientsService/Repository
    # Ejemplo: success = _patients_service.delete(patient_id)
    # if not success:
    #     abort(500, description="Error al eliminar el paciente.")
    # return "", 204
    # --- Placeholder ---
    print(f"TODO: Implementar PatientsService.delete({patient_id})")
    return "", 204 # Simula éxito No Content
    # --- Fin Placeholder ---

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

    # El servicio maneja la lógica de 'crear si no existe' por serial
    # Nota: Aquí no se asigna a paciente, solo se registra.
    try:
        # Necesitas un método `create` o `register` en DevicesService
        # device = _devices_service.create(**data)
        # return _device_out.dump(device), 201
        # --- Placeholder ---
        print(f"TODO: Implementar DevicesService.create({data})")
        # Simula creación exitosa devolviendo datos de entrada + ID ficticio
        return {"id": 999, **data, "status": "new", "patient_id": None}, 201
        # --- Fin Placeholder ---
    except Exception as e: # Podría fallar si el serial ya existe y no usas upsert
        abort(409, description=f"Conflicto al registrar dispositivo. ¿Serial duplicado? ({e})")

@admin_bp.get("/devices")
@admin_required()
def list_devices_admin():
    """Lista todos los dispositivos registrados."""
    # Necesitas un método `list_all` en DevicesService/Repository
    # devices = _devices_service.list_all()
    # return {"items": _device_out_many.dump(devices)}, 200
    # --- Placeholder ---
    print("TODO: Implementar DevicesService.list_all()")
    return {"items": []}, 200
    # --- Fin Placeholder ---

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
    if not _devices_service.get_by_id(device_id):
        abort(404, description="Dispositivo no encontrado.")

    payload = request.get_json() or {}
    try:
        data = _device_update_in.load(payload) # Valida los campos a actualizar (ej. status, model)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # Necesitas un método `update` en DevicesService/Repository
    # updated_device = _devices_service.update(device_id, data)
    # if not updated_device:
    #     abort(500, "Error al actualizar dispositivo.")
    # return _device_out.dump(updated_device), 200
    # --- Placeholder ---
    print(f"TODO: Implementar DevicesService.update({device_id}, {data})")
    updated_device = _devices_service.get_by_id(device_id) # Lee de nuevo
    if updated_device: # Simula actualización local para respuesta
        for key, value in data.items():
            if hasattr(updated_device, key): setattr(updated_device, key, value)
    return _device_out.dump(updated_device), 200
    # --- Fin Placeholder ---

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
    if not _devices_service.get_by_id(device_id):
        abort(404, description="Dispositivo no encontrado.")

    # Necesitas un método `delete` en DevicesService/Repository
    # Considera las implicaciones: ¿borrar lecturas/telemetría (CASCADE)? ¿O solo marcar como 'retired'?
    # success = _devices_service.delete(device_id)
    # if not success:
    #     abort(500, description="Error al eliminar el dispositivo.")
    # return "", 204
    # --- Placeholder ---
    print(f"TODO: Implementar DevicesService.delete({device_id}) - ¡Considerar consecuencias!")
    return "", 204 # Simula éxito No Content
    # --- Fin Placeholder ---

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
     # Necesitas un método `get` en AlertsService/Repository
     # alert = _alerts_service.get(alert_id)
     # if not alert:
     #     abort(404, description="Alerta no encontrada.")
     # return _alert_out.dump(alert), 200
     # --- Placeholder ---
     print(f"TODO: Implementar AlertsService.get({alert_id})")
     # Simula encontrar una alerta
     return {"id": alert_id, "message": "Placeholder alert"}, 200
     # --- Fin Placeholder ---


@admin_bp.post("/alerts/<int:alert_id>/acknowledge")
@admin_required()
def acknowledge_alert(alert_id: int):
    """Marca una alerta como reconocida por el admin actual."""
    user_id = get_jwt()["sub"] # Obtiene el ID del admin desde el token

    payload = request.get_json() or {}
    try:
        # Podrías tener un schema para notas opcionales al reconocer
        data = _alert_ack_in.load(payload) # Asume que puede estar vacío o tener { "notes": "..." }
    except ValidationError as err:
        return {"messages": err.messages}, 400

    # Necesitas un método `acknowledge` en AlertsService/Repository
    # updated_alert = _alerts_service.acknowledge(alert_id, user_id, data.get("notes"))
    # if not updated_alert:
    #     abort(404, description="Alerta no encontrada o ya reconocida.") # O 409 Conflict
    # return _alert_out.dump(updated_alert), 200
    # --- Placeholder ---
    print(f"TODO: Implementar AlertsService.acknowledge({alert_id}, user_id={user_id}, notes={payload.get('notes')})")
    # Simula éxito devolviendo detalle placeholder
    return {"id": alert_id, "message": "Placeholder", "acknowledged_by": user_id, "acknowledged_at": "now"}, 200
    # --- Fin Placeholder ---


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
    # Necesitas un schema _threshold_out_many
    # return {"items": _threshold_out_many.dump(thresholds)}, 200 # Usa el schema adecuado
    return {"items": thresholds}, 200 # Respuesta directa mientras creas schema

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
    # return {"items": _threshold_out_many.dump(thresholds)}, 200 # Usa el schema adecuado
    return {"items": thresholds}, 200

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