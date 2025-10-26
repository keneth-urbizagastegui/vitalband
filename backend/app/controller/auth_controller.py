from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from ..model.dto.request_schemas import LoginRequest

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/login")
def login():
    payload = request.get_json() or {}
    data = LoginRequest().load(payload)
    # TODO: validar usuario real; por ahora "demo"
    if data["email"] and data["password"]:
        token = create_access_token(identity=data["email"])
        return {"access_token": token}, 200
    return {"message": "invalid credentials"}, 401
