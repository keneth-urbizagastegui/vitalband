from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, cors, jwt
# from .model.models import User # Mantenemos esto comentado aquí

from .controller.auth_controller import auth_bp
from .controller.client_controller import client_bp
from .controller.admin_controller import admin_bp
from .controller.telemetry_controller import telemetry_bp
from .controller.chatbot_controller import chatbot_bp

import logging # Import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def create_app(config_object: type[Config] | str = Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # --- Debug Prints (Mantenemos por ahora) ---
    log.info(f"DEBUG (Antes Init): Valor de JWT_CSRF_IN_ACCESS_TOKEN cargado: {app.config.get('JWT_CSRF_IN_ACCESS_TOKEN')}")
    log.info(f"DEBUG (Antes Init): Valor de JWT_COOKIE_CSRF_PROTECT cargado: {app.config.get('JWT_COOKIE_CSRF_PROTECT')}")
    log.info(f"DEBUG (Antes Init): Valor de JWT_TOKEN_LOCATION cargado: {app.config.get('JWT_TOKEN_LOCATION')}")
    # --- FIN Debug ---

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS_LIST")}},
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", False),
    )
    jwt.init_app(app)

    log.info("--- REGISTRANDO EL USER LOADER ---")

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        log.info("\n--- INICIO USER LOADER ---")
        from .model.models import User # Importación local
        identity = jwt_data.get("sub")
        if not identity:
            log.error("USER_LOADER_ERROR: No se encontró 'sub' (identity) en el token.")
            return None
        try:
            user_id = int(identity)
            log.info(f"USER_LOADER_INFO: Buscando usuario con ID: {user_id} (Tipo: {type(user_id)})")
            user = User.query.get(user_id)
            if not user:
                log.warning(f"USER_LOADER_WARNING: Usuario con ID {user_id} no encontrado en la BD.")
                return None
            log.info(f"USER_LOADER_SUCCESS: Usuario {user.email} cargado exitosamente.")
            log.info("--- FIN USER LOADER ---\n")
            return user
        except ValueError:
            log.error(f"USER_LOADER_ERROR: 'sub' del token no era un entero válido: {identity}")
            return None
        except Exception as e:
            log.error(f"USER_LOADER_ERROR: Error inesperado al cargar usuario: {e}")
            return None

    # --- Handlers de errores JWT con Logging Adicional ---
    @jwt.unauthorized_loader
    def _missing_jwt(reason: str):
        # Este se llama si NO se encuentra un token donde se espera (según JWT_TOKEN_LOCATION)
        log.warning(f"JWT Unauthorized: No se encontró token o tuvo formato incorrecto. Razón: {reason}")
        return jsonify({"message": "Acceso no autorizado: Falta token o formato incorrecto.", "reason": reason}), 401

    @jwt.invalid_token_loader
    def _invalid_jwt(reason: str):
        # Este se llama si el token se encontró pero falló alguna validación (firma, claims básicos)
        log.error(f"JWT Invalid: El token es inválido. Razón: {reason}")
        return jsonify({"message": "Token inválido.", "reason": reason}), 401

    @jwt.expired_token_loader
    def _expired_jwt(jwt_header, jwt_payload):
        log.warning("JWT Expired: El token ha expirado.")
        return jsonify({"message": "Token ha expirado."}), 401

    @jwt.needs_fresh_token_loader
    def _needs_fresh(jwt_header, jwt_payload):
        # No aplica si no usas fresh tokens
        log.warning("JWT Needs Fresh: Se requiere un token 'fresh'.")
        return jsonify({"message": "Se requiere un token 'fresh'."}), 401
    # --- Fin Handlers Modificados ---

    # Blueprints con prefijo (centralizado acá)
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(client_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    app.register_blueprint(telemetry_bp, url_prefix="/api/v1")
    app.register_blueprint(chatbot_bp, url_prefix="/api/v1/chatbot")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app

