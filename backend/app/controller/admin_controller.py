from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.patients_service import PatientsService
from ..model.dto.request_schemas import PatientCreateRequest
from ..model.dto.response_schemas import PatientResponse

admin_bp = Blueprint("admin", __name__)
_patients_service = PatientsService()

@admin_bp.post("/patients")
@jwt_required()
def create_patient():
    payload = request.get_json() or {}
    data = PatientCreateRequest().load(payload)
    p = _patients_service.create_patient(full_name=data["full_name"], email=data.get("email"))
    return PatientResponse().dump(p), 201
