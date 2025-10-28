# backend/app/controller/auth_controller.py

import logging 
from flask import Blueprint, request, abort, jsonify, current_app # <-- Import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

# ... (El resto de tus imports: request_schemas, response_schemas, User, db) ...
from ..model.dto.request_schemas import (
    LoginRequest,
    RegisterRequest, 
    ForgotPasswordRequest, 
    ResetPasswordRequest
)
from ..model.dto.response_schemas import UserResponse 
from ..model.models import User
from ..extensions import db 

auth_bp = Blueprint("auth", __name__) 

# Instancias de Schemas
_login_in = LoginRequest()
_register_in = RegisterRequest() 
_forgot_password_in = ForgotPasswordRequest() 
_reset_password_in = ResetPasswordRequest() 
_user_out = UserResponse() 

# Configura un logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # <-- Nos aseguramos de que el nivel de log esté bien


@auth_bp.post("/login")
def login():
    """Autentica un usuario y devuelve un token JWT."""
    payload = request.get_json(silent=True) or {}

    try:
        data = _login_in.load(payload)
    except ValidationError as err:
        logger.warning(f"Intento de login fallido (validación): {err.messages}")
        return {"message": "Credenciales inválidas"}, 401

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.pass_hash, password):
        user_id = user.id
        role = user.role
        additional = {"role": role}
        token = create_access_token(identity=user_id, additional_claims=additional)
        logger.info(f"Login exitoso para usuario {user_id} ({email})")
        
        user_info = {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        
        # Log que podemos quitar después
        logger.error(f"PASO 1 (BACKEND): Token creado y enviado: {token}")
        
        return {"access_token": token, "user": user_info}, 200
    else:
        logger.warning(f"Intento de login fallido (credenciales) para email: {email}")
        return {"message": "Credenciales inválidas"}, 401


# ... (Tus otras rutas: /register, /forgot-password, /reset-password, /me se mantienen igual) ...

@auth_bp.post("/register")
def register():
    """Registra un nuevo usuario (cliente por defecto)."""
    payload = request.get_json(silent=True) or {}

    try:
        data = _register_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    email = data["email"].strip().lower()
    password = data["password"] 
    name = data.get("name", "") 

    if User.query.filter_by(email=email).first():
        logger.warning(f"Intento de registro fallido (email ya existe): {email}")
        abort(409, description="El correo electrónico ya está registrado.") 

    password_hash = generate_password_hash(password)

    new_user = User(
        name=name,
        email=email,
        pass_hash=password_hash,
        role='client' 
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user) 
        logger.info(f"Nuevo usuario registrado: {new_user.id} ({email})")

        additional = {"role": new_user.role}
        token = create_access_token(identity=new_user.id, additional_claims=additional)

        return {
            "message": "Usuario registrado exitosamente.",
            "user": _user_out.dump(new_user),
            "access_token": token 
            }, 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al registrar usuario {email}: {e}")
        abort(500, description="Error interno al registrar el usuario.")


@auth_bp.post("/forgot-password")
def forgot_password():
    """Inicia el proceso de recuperación de contraseña (envía email)."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _forgot_password_in.load(payload) 
    except ValidationError as err:
        return {"messages": err.messages}, 400

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        logger.info(f"Solicitud de reseteo de contraseña para {email}. TODO: Enviar email.")
        return {"message": "Si tu correo está registrado, recibirás instrucciones para restablecer tu contraseña."}, 200
    else:
        logger.warning(f"Intento de reseteo de contraseña para email no registrado: {email}")
        return {"message": "Si tu correo está registrado, recibirás instrucciones para restablecer tu contraseña."}, 200


@auth_bp.post("/reset-password")
def reset_password():
    """Completa el proceso de recuperación de contraseña."""
    payload = request.get_json(silent=True) or {}
    try:
        data = _reset_password_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    reset_token = data["token"]
    new_password = data["new_password"]
    
    logger.info(f"Intento de reseteo de contraseña con token {reset_token}. TODO: Implementar validación y actualización.")
    return {"message": "Contraseña actualizada exitosamente (Placeholder - Implementar Lógica)."}, 200


@auth_bp.get("/me")
@jwt_required()
def get_me():
    """Obtiene la información básica del usuario autenticado."""
    user_id = get_jwt_identity()
    claims = get_jwt()
    user_role = claims.get('role')

    if not user_id or not user_role:
        logger.error("Token JWT inválido o incompleto detectado en /me")
        return {"message": "Token inválido o incompleto"}, 401

    user = User.query.get(user_id)
    if not user:
        logger.error(f"Usuario con ID {user_id} del token no encontrado en la base de datos.")
        return {"message": "Usuario asociado al token no encontrado"}, 401

    response_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }
    return response_data, 200


# --- RUTA DE DEBUG AÑADIDA ---
@auth_bp.get("/debug-config")
def debug_config():
    """Devuelve el valor de la config JWT_CSRF_PROTECT_METHODS."""
    try:
        # Accede a la configuración de la aplicación Flask actual
        config_value = current_app.config.get("JWT_CSRF_PROTECT_METHODS")
        default_value = current_app.config.get("JWT_CSRF_METHODS") # Esta es la config por defecto
        
        return jsonify(
            config_cargada=config_value,
            config_por_defecto=default_value
        ), 200
    except Exception as e:
        logger.error(f"Error en debug-config: {e}")
        return jsonify(error=str(e)), 500
# --- FIN DE RUTA DE DEBUG ---

