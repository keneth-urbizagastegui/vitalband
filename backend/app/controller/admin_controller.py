from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..services.patients_service import PatientsService
from ..model.dto.request_schemas import PatientCreateRequest
from ..model.dto.response_schemas import PatientResponse

admin_bp = Blueprint("admin", __name__) 
_patients_service = PatientsService()
_patient_create_in = PatientCreateRequest()
_patient_out = PatientResponse()

@admin_bp.post("/patients")
@jwt_required()
def create_patient():
    payload = request.get_json() or {}
    data = _patient_create_in.load(payload)
    p = _patients_service.create_patient(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data.get("email"),
        phone=data.get("phone"),
        birthdate=data.get("birthdate"),
        sex=data.get("sex") or "unknown",
        height_cm=data.get("height_cm"),
        weight_kg=data.get("weight_kg"),
        user_id=data.get("user_id"),
    )
    return _patient_out.dump(p), 201
