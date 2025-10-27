from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from ..model.dto.request_schemas import LoginRequest

auth_bp = Blueprint("auth", __name__)
_login_in = LoginRequest()

@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}

    # Si falla la validación (email inválido/vacío, etc.), respondemos 401
    try:
        data = _login_in.load(payload)
    except ValidationError:
        return {"message": "invalid credentials"}, 401

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # TODO: Reemplazar por validación real contra tabla users (hash de password).
    # Demo: si llegan email y password no vacíos, emitimos token.
    if email and password:
        role = "admin" if "admin" in email else "client"
        additional = {"role": role, "patient_id": None}
        token = create_access_token(identity=email, additional_claims=additional)
        return {"access_token": token}, 200

    return {"message": "invalid credentials"}, 401
