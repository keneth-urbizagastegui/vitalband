from flask import Blueprint, request
# Importa check_password_hash si implementas la validación real
# from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from ..model.dto.request_schemas import LoginRequest
from ..model.models import User

auth_bp = Blueprint("auth", __name__)
_login_in = LoginRequest()

@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}

    try:
        data = _login_in.load(payload)
    except ValidationError:
        return {"message": "invalid credentials"}, 401

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # --- Implementación REAL (Recomendada) ---
    # user = User.query.filter_by(email=email).first()
    # # ¡IMPORTANTE! Necesitas importar check_password_hash
    # if user and check_password_hash(user.pass_hash, password):
    #     role = user.role
    #     user_id = user.id
    #     additional = {"role": role}
    #     # Pasa el ID del usuario como identity para que sea el 'sub' claim
    #     token = create_access_token(identity=user_id, additional_claims=additional)
    #     return {"access_token": token}, 200
    # else:
    #     return {"message": "invalid credentials"}, 401
    # --- ---

    # --- Lógica DEMO actual (Corregida, pero aún insegura para prod) ---
    if email and password: # Validación demo simple
        user_demo = User.query.filter_by(email=email).first()
        if not user_demo: # Si el email demo no existe en la BD
             return {"message": "invalid credentials"}, 401

        # ¡Aún no valida contraseña!
        user_id = user_demo.id
        role = user_demo.role # Obtener rol real de la BD, incluso para demo

        additional = {"role": role}
        # CORRECCIÓN: Quitar 'subject'. Pasar user_id como identity.
        token = create_access_token(identity=user_id, additional_claims=additional)
        return {"access_token": token}, 200
    # --- ---

    return {"message": "invalid credentials"}, 401


# --- Endpoint /me (sin cambios necesarios aquí, pero asegúrate que usa 'identity') ---
@auth_bp.get("/me")
@jwt_required()
def get_me():
    print("--- Entrando a /me ---") # DEBUG
    user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get('role')
    print(f"DEBUG: user_id from token: {user_id}") # DEBUG
    print(f"DEBUG: user_role from token: {user_role}") # DEBUG

    if not user_id or not user_role:
        print("ERROR: user_id o user_role faltan en el token") # DEBUG
        return {"message": "Token inválido o incompleto"}, 401

    user = User.query.get(user_id)
    print(f"DEBUG: User found in DB: {user}") # DEBUG
    if not user:
        print(f"ERROR: Usuario con ID {user_id} no encontrado en BD") # DEBUG
        return {"message": "User associated with token not found"}, 401

    response_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }
    print(f"DEBUG: Devolviendo datos: {response_data}") # DEBUG
    return response_data, 200