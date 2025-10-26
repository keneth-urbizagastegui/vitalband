from flask import Flask
from .config import Config
from .extensions import db, migrate, cors, jwt
from .controller.auth_controller import auth_bp
from .controller.client_controller import client_bp
from .controller.admin_controller import admin_bp

def create_app(config_object: type[Config] | str = Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS_LIST")}})
    jwt.init_app(app)

    # Blueprints con prefijo
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(client_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
