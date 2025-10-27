import os
import sys
import pytest

# --- Permite importar "app" cuando corremos pytest desde backend/ ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, Config  # noqa: E402


class TestConfig(Config):
    TESTING = True
    # Si quisieras una BD separada para tests, descomenta y ajusta:
    # SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # o bien apunta a otra BD MySQL de pruebas:
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/vitalband_test"


@pytest.fixture(scope="session")
def app():
    # Asegura que Flask CLI sepa dónde está la app (útil en algunos entornos)
    os.environ.setdefault("FLASK_APP", "run.py")
    application = create_app(TestConfig)
    ctx = application.app_context()
    ctx.push()
    yield application
    ctx.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def token(client):
    """Obtiene un JWT válido (login demo)."""
    payload = {"email": "admin@vitalband.local", "password": "Admin123!"}
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200, res.get_json()
    return res.get_json()["access_token"]


@pytest.fixture()
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}
