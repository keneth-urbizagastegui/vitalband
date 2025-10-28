from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, cors, jwt

from .controller.auth_controller import auth_bp
from .controller.client_controller import client_bp
from .controller.admin_controller import admin_bp
from .controller.telemetry_controller import telemetry_bp  # nuevo
from .controller.chatbot_controller import chatbot_bp

def create_app(config_object: type[Config] | str = Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS_LIST")}},
        supports_credentials=app.config.get("CORS_SUPPORTS_CREDENTIALS", False),
    )
    jwt.init_app(app)

    # Handlers de errores JWT
    @jwt.unauthorized_loader
    def _missing_jwt(reason: str):
        return jsonify({"message": "Missing or invalid JWT", "reason": reason}), 401

    @jwt.invalid_token_loader
    def _invalid_jwt(reason: str):
        return jsonify({"message": "Invalid token", "reason": reason}), 401

    @jwt.expired_token_loader
    def _expired_jwt(jwt_header, jwt_payload):
        return jsonify({"message": "Token has expired"}), 401

    @jwt.needs_fresh_token_loader
    def _needs_fresh(jwt_header, jwt_payload):
        return jsonify({"message": "Fresh token required"}), 401

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
