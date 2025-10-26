from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..model.dto.response_schemas import PatientResponse, MetricResponse

client_bp = Blueprint("client", __name__)
_patients_service = PatientsService()
_metrics_service = MetricsService()

@client_bp.get("/patients")
@jwt_required(optional=True)
def list_patients():
    patients = _patients_service.list_patients()
    return {"items": PatientResponse(many=True).dump(patients)}, 200

@client_bp.get("/metrics/<int:device_id>/last24h")
@jwt_required(optional=True)
def metrics_last24h(device_id: int):
    metrics = _metrics_service.last_24h_for_device(device_id)
    return {"items": MetricResponse(many=True).dump(metrics)}, 200
