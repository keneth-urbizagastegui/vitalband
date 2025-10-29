import os
from datetime import timedelta

def _bool(x: str | None, default: bool = False) -> bool:
    if x is None:
        return default
    return x.strip().lower() in {"1", "true", "t", "yes", "y"}

class Config:
    # Flask / JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "480"))  # 8h por defecto
    )

    # --- RESTAURAR Y ASEGURAR QUE TODO ESTÉ EN FALSE ---
    JWT_CSRF_PROTECT_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    JWT_CSRF_IN_ACCESS_TOKEN = False
    JWT_CSRF_IN_REFRESH_TOKEN = False
    JWT_COOKIE_CSRF_PROTECT = False
    # --- FIN RESTAURACIÓN ---

    # --- NUEVO: Especificar explícitamente la ubicación del token ---
    JWT_TOKEN_LOCATION = ["headers"] # Asegura que busque en 'Authorization: Bearer'
    # --- FIN NUEVO ---

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "vitalband")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    }

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    CORS_ORIGINS_LIST = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
    CORS_SUPPORTS_CREDENTIALS = _bool(os.getenv("CORS_SUPPORTS_CREDENTIALS", "0"))

    # Debug
    DEBUG = _bool(os.getenv("FLASK_DEBUG", "1"))

    # JSON
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = _bool(os.getenv("JSON_PRETTY", "0"))
