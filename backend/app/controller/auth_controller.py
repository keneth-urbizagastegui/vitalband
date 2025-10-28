# backend/app/controller/auth_controller.py

import logging # Para logging en lugar de print
from flask import Blueprint, request, abort, jsonify
# Importa funciones para hashear y verificar contraseñas
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

# Schemas de Request (necesitarás crearlos o completarlos)
from ..model.dto.request_schemas import (
    LoginRequest,
    RegisterRequest, # ¡Nuevo! Necesitas crearlo
    ForgotPasswordRequest, # ¡Nuevo! Necesitas crearlo
    ResetPasswordRequest # ¡Nuevo! Necesitas crearlo
)
# Schema de Respuesta (si lo necesitas para el registro)
from ..model.dto.response_schemas import UserResponse # ¡Nuevo! Necesitas crearlo

from ..model.models import User
from ..extensions import db # Importa db para operaciones de registro

auth_bp = Blueprint("auth", __name__) # Mantenemos prefijo en __init__.py

# Instancias de Schemas
_login_in = LoginRequest()
_register_in = RegisterRequest() # Nuevo
_forgot_password_in = ForgotPasswordRequest() # Nuevo
_reset_password_in = ResetPasswordRequest() # Nuevo
_user_out = UserResponse() # Nuevo

# Configura un logger
logger = logging.getLogger(__name__)

@auth_bp.post("/login")
def login():
    """Autentica un usuario y devuelve un token JWT."""
    payload = request.get_json(silent=True) or {}

    try:
        data = _login_in.load(payload)
    except ValidationError as err:
        logger.warning(f"Intento de login fallido (validación): {err.messages}")
        # Devuelve un error más genérico por seguridad
        return {"message": "Credenciales inválidas"}, 401

    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    # --- Implementación REAL (Habilitada) ---
    user = User.query.filter_by(email=email).first()

    # Verifica si el usuario existe Y si la contraseña coincide con el hash
    if user and check_password_hash(user.pass_hash, password):
        user_id = user.id
        role = user.role
        additional = {"role": role}
        # Pasa el ID del usuario como identity
        token = create_access_token(identity=user_id, additional_claims=additional)
        logger.info(f"Login exitoso para usuario {user_id} ({email})")
        # Considera devolver también información básica del usuario si el frontend la necesita inmediatamente
        user_info = {
            "id": user.id,
            "email": user.email,
            "role": user.role
            # Añade 'name' si lo tienes en el modelo User y lo quieres devolver
            # "name": user.name
        }
        return {"access_token": token, "user": user_info}, 200
    else:
        logger.warning(f"Intento de login fallido (credenciales) para email: {email}")
        return {"message": "Credenciales inválidas"}, 401
    # --- ---

@auth_bp.post("/register")
def register():
    """Registra un nuevo usuario (cliente por defecto)."""
    payload = request.get_json(silent=True) or {}

    try:
        # Valida name, email, password (y quizás confirmación de password)
        data = _register_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    email = data["email"].strip().lower()
    password = data["password"] # Asume que el schema ya valida longitud/complejidad
    name = data.get("name", "") # Asume que 'name' viene en RegisterRequest

    # 1. Verificar si el email ya existe
    if User.query.filter_by(email=email).first():
        logger.warning(f"Intento de registro fallido (email ya existe): {email}")
        abort(409, description="El correo electrónico ya está registrado.") # 409 Conflict

    # 2. Hashear la contraseña
    password_hash = generate_password_hash(password)

    # 3. Crear el nuevo usuario (rol 'client' por defecto)
    new_user = User(
        name=name,
        email=email,
        pass_hash=password_hash,
        role='client' # Por defecto para el registro público
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user) # Para obtener el ID asignado
        logger.info(f"Nuevo usuario registrado: {new_user.id} ({email})")

        # Opcional: Crear token JWT inmediatamente para loguear al usuario
        additional = {"role": new_user.role}
        token = create_access_token(identity=new_user.id, additional_claims=additional)

        # Devuelve info del usuario creado y el token
        return {
            "message": "Usuario registrado exitosamente.",
            "user": _user_out.dump(new_user),
            "access_token": token # Opcional, si quieres auto-login
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
        data = _forgot_password_in.load(payload) # Valida { "email": "..." }
    except ValidationError as err:
        return {"messages": err.messages}, 400

    email = data["email"].strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        # --- Lógica Pendiente ---
        # 1. Generar un token de reseteo seguro y con expiración
        #    (podrías usar Flask-JWT-Extended para esto también,
        #     o un token específico con itsdangerous).
        # reset_token = create_reset_token(identity=user.id) # Función hipotética
        # 2. Construir la URL de reseteo (ej. https://frontend.com/reset-password?token=...)
        # reset_url = f"https://tu-frontend.com/reset-password?token={reset_token}"
        # 3. Enviar un email al usuario con esa URL.
        #    Necesitarás configurar un servicio de envío de emails (ej. Flask-Mail, SendGrid).
        # send_password_reset_email(user.email, reset_url) # Función hipotética
        # --- Fin Lógica Pendiente ---
        logger.info(f"Solicitud de reseteo de contraseña para {email}. TODO: Enviar email.")
        # Devuelve siempre éxito para no revelar si un email existe o no
        return {"message": "Si tu correo está registrado, recibirás instrucciones para restablecer tu contraseña."}, 200
    else:
        logger.warning(f"Intento de reseteo de contraseña para email no registrado: {email}")
        # Devuelve el mismo mensaje genérico
        return {"message": "Si tu correo está registrado, recibirás instrucciones para restablecer tu contraseña."}, 200


@auth_bp.post("/reset-password")
def reset_password():
    """Completa el proceso de recuperación de contraseña."""
    payload = request.get_json(silent=True) or {}
    try:
        # Valida { "token": "...", "new_password": "..." }
        data = _reset_password_in.load(payload)
    except ValidationError as err:
        return {"messages": err.messages}, 400

    reset_token = data["token"]
    new_password = data["new_password"]

    # --- Lógica Pendiente ---
    # 1. Validar el token de reseteo (verificar firma, expiración).
    #    Si usaste JWT, podrías usar `decode_token`. Si usaste itsdangerous, `serializer.loads`.
    # try:
    #     user_id = verify_reset_token(reset_token) # Función hipotética, devuelve user_id o lanza excepción
    # except Exception as token_error: # Captura TokenExpired, BadSignature, etc.
    #     logger.warning(f"Intento de reseteo con token inválido/expirado: {token_error}")
    #     abort(400, description="El enlace de restablecimiento es inválido o ha expirado.")
    #
    # 2. Buscar al usuario por user_id.
    # user = User.query.get(user_id)
    # if not user:
    #     # Raro, el token era válido pero el usuario ya no existe
    #     logger.error(f"Usuario {user_id} de token de reseteo válido no encontrado en BD.")
    #     abort(404, description="Usuario no encontrado.")
    #
    # 3. Hashear la nueva contraseña.
    # new_password_hash = generate_password_hash(new_password)
    #
    # 4. Actualizar el hash en la base de datos.
    # user.pass_hash = new_password_hash
    # try:
    #     db.session.commit()
    #     logger.info(f"Contraseña restablecida para usuario {user_id}")
    #     # Opcional: Invalidar tokens JWT activos existentes para este usuario
    #     return {"message": "Contraseña actualizada exitosamente."}, 200
    # except Exception as e:
    #     db.session.rollback()
    #     logger.error(f"Error al actualizar contraseña para usuario {user_id}: {e}")
    #     abort(500, "Error interno al actualizar la contraseña.")
    # --- Fin Lógica Pendiente ---

    logger.info(f"Intento de reseteo de contraseña con token {reset_token}. TODO: Implementar validación y actualización.")
    # Placeholder de éxito temporal
    return {"message": "Contraseña actualizada exitosamente (Placeholder - Implementar Lógica)."}, 200


# --- Endpoint /me (sin cambios funcionales, solo se quitan prints) ---
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
        # Podría significar que el usuario fue eliminado después de que el token fue emitido
        return {"message": "Usuario asociado al token no encontrado"}, 401

    response_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role
        # Añade 'name' si lo tienes en el modelo User
        # "name": user.name
    }
    return response_data, 200