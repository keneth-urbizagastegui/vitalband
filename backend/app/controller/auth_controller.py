import logging
from flask import Blueprint, request, abort, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
# Asegúrate que create_access_token se importa correctamente
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

# Schemas
from ..model.dto.request_schemas import (
    LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from ..model.dto.response_schemas import UserResponse

from ..model.models import User
from ..extensions import db
from ..services.patients_service import PatientsService

auth_bp = Blueprint("auth", __name__)

# Instancias de Schemas
_login_in = LoginRequest()
_register_in = RegisterRequest()
_forgot_password_in = ForgotPasswordRequest()
_reset_password_in = ResetPasswordRequest()
_user_out = UserResponse()
_patients_service = PatientsService()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Mantenemos logging visible

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
        user_id_int = user.id # Guardamos el ID como entero
        role = user.role
        additional = {"role": role}

        # --- DEBUG FINAL (Mantenemos) ---
        csrf_config_value = current_app.config.get('JWT_CSRF_IN_ACCESS_TOKEN')
        logger.info(f"DEBUG (auth_controller): Valor de JWT_CSRF_IN_ACCESS_TOKEN antes de crear token: {csrf_config_value}")
        # --- FIN DEBUG ---

        # --- MODIFICACIÓN: Convertir identity a string ---
        user_id_str = str(user_id_int) # Convertimos a string
        token = create_access_token(identity=user_id_str, additional_claims=additional) # Usamos el string
        # --- FIN MODIFICACIÓN ---

        logger.info("Token creado y enviado")
        logger.info(f"Login exitoso para usuario {user_id_int} ({email})")

        user_info = {
            "id": user_id_int, # Devolvemos el ID como número al frontend
            "email": user.email,
            "role": user.role
            # "name": user.name
        }
        return {"access_token": token, "user": user_info}, 200
    else:
        logger.warning(f"Intento de login fallido (credenciales) para email: {email}")
        return {"message": "Credenciales inválidas"}, 401

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

    new_user = User(name=name, email=email, pass_hash=password_hash, role='client')

    try:
        db.session.add(new_user)
        db.session.commit()
        db.session.refresh(new_user)
        logger.info(f"Nuevo usuario registrado: {new_user.id} ({email})")

        # --- INICIO DE LA MODIFICACIÓN ---
        # Ahora, crea automáticamente el perfil de paciente asociado
        try:
            # Extrae nombres del campo 'name'
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "" # Apellido opcional

            _patients_service.create_patient(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                email=email # Puede usar el mismo email
            )
            logger.info(f"Perfil de paciente creado automáticamente para user_ID {new_user.id}")
        except Exception as e:
            # Si esto falla, el registro de usuario debe deshacerse (rollback)
            logger.error(f"¡FALLO CRÍTICO! El usuario {new_user.id} se creó, pero su perfil de paciente falló: {e}")
            # Lanza el error para que el 'except' de abajo lo capture y haga rollback
            raise e
        # --- FIN DE LA MODIFICACIÓN ---

        additional = {"role": new_user.role}
        user_id_str_reg = str(new_user.id) 
        token = create_access_token(identity=user_id_str_reg, additional_claims=additional) 

        return {
            "message": "Usuario registrado exitosamente.",
            "user": _user_out.dump(new_user),
            "access_token": token
            }, 201

    except Exception as e:
        db.session.rollback() # Esto deshará la creación del 'User' si el 'Patient' falla
        logger.error(f"Error al registrar usuario {email} o su perfil: {e}")
        abort(500, description="Error interno al registrar el usuario.")

# ... (resto de las funciones: forgot_password, reset_password, get_me, debug_config sin cambios) ...

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

    # --- Lógica Pendiente ---
    logger.info(f"Intento de reseteo de contraseña con token {reset_token}. TODO: Implementar validación y actualización.")
    return {"message": "Contraseña actualizada exitosamente (Placeholder - Implementar Lógica)."}, 200


@auth_bp.get("/me")
@jwt_required()
def get_me():
    """Obtiene la información básica del usuario autenticado."""
    # --- MODIFICACIÓN: get_jwt_identity ahora devolverá string ---
    user_id_str = get_jwt_identity()
    # --- FIN MODIFICACIÓN ---
    claims = get_jwt()
    user_role = claims.get('role')

    # Validación extra por si acaso
    if not user_id_str or not isinstance(user_id_str, str):
        logger.error(f"Error en /me: get_jwt_identity() no devolvió un string: {user_id_str}")
        return {"message": "Identidad de token inválida."}, 401
    if not user_role:
        logger.error("Token JWT incompleto detectado en /me (falta role)")
        return {"message": "Token incompleto"}, 401

    try:
        # --- MODIFICACIÓN: Convertir de vuelta a int para buscar en BD ---
        user_id = int(user_id_str)
        # --- FIN MODIFICACIÓN ---
    except ValueError:
        logger.error(f"Error en /me: La identidad del token no es un entero válido: {user_id_str}")
        return {"message": "Identidad de token inválida."}, 401

    user = User.query.get(user_id)
    if not user:
        logger.error(f"Usuario con ID {user_id} del token no encontrado en la base de datos.")
        return {"message": "Usuario asociado al token no encontrado"}, 401

    response_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role
        # "name": user.name
    }
    return response_data, 200


@auth_bp.get("/debug-config")
def get_debug_config():
    """Ruta de debug para verificar la config JWT cargada."""
    config_methods = current_app.config.get("JWT_CSRF_PROTECT_METHODS")
    in_access_token = current_app.config.get("JWT_CSRF_IN_ACCESS_TOKEN")
    cookie_csrf_protect = current_app.config.get("JWT_COOKIE_CSRF_PROTECT")
    token_location = current_app.config.get("JWT_TOKEN_LOCATION")

    return jsonify({
        "JWT_CSRF_PROTECT_METHODS": config_methods,
        "JWT_CSRF_IN_ACCESS_TOKEN": in_access_token,
        "JWT_COOKIE_CSRF_PROTECT": cookie_csrf_protect,
        "JWT_TOKEN_LOCATION": token_location
    }), 200
