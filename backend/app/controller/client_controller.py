from flask import Blueprint
from flask_jwt_extended import jwt_required
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..model.dto.response_schemas import PatientResponse, ReadingResponse

client_bp = Blueprint("client", __name__) 
_patients_service = PatientsService()
_metrics_service = MetricsService()

_patients_out_many = PatientResponse(many=True)
_readings_out_many = ReadingResponse(many=True)

@client_bp.get("/patients")
@jwt_required(optional=True)
def list_patients():
    patients = _patients_service.list_patients()
    return {"items": _patients_out_many.dump(patients)}, 200

# Nuevo nombre: readings
@client_bp.get("/readings/<int:device_id>/last24h")
@jwt_required(optional=True)
def readings_last24h(device_id: int):
    readings = _metrics_service.last_24h_for_device(device_id)
    return {"items": _readings_out_many.dump(readings)}, 200

# Alias de compatibilidad con la versión anterior
@client_bp.get("/metrics/<int:device_id>/last24h")
@jwt_required(optional=True)
def metrics_last24h_alias(device_id: int):
    readings = _metrics_service.last_24h_for_device(device_id)
    return {"items": _readings_out_many.dump(readings)}, 200
