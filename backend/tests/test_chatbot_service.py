import pytest
from unittest import mock

from app.services.chatbot_service import ChatbotService


def test_chatbot_system_prompt_has_safety_rule():
    """El system_prompt debe contener la regla de seguridad 'NUNCA diagnostiques'."""
    service = ChatbotService()
    assert "NUNCA diagnostiques" in service.system_prompt


def test_get_reply_does_not_duplicate_prompt():
    """Verifica que la regla 'NUNCA diagnostiques' aparezca solo una vez en el prompt enviado al modelo."""
    service = ChatbotService()

    # Simula el contexto del usuario para evitar acceder a BD/servicios reales
    fake_ctx = {
        "patient": {"full_name": "Paciente Test"},
        "latest_reading": {"heart_rate_bpm": 72, "spo2_pct": 97, "temp_c": 36.7},
        "pending_alerts": [],
        "thresholds": {
            "heart_rate": {"min_value": 50, "max_value": 120},
            "spo2": {"min_value": 92, "max_value": 100},
            "temperature": {"min_value": 35.5, "max_value": 38.0},
        },
    }

    # Patch: get_context_for_user devuelve nuestro diccionario controlado
    service.get_context_for_user = mock.Mock(return_value=fake_ctx)

    # Prepara un mock para generate_content que capture el prompt
    class DummyResponse:
        def __init__(self, text):
            self.text = text

    service.model = mock.Mock()
    service.model.generate_content = mock.Mock(return_value=DummyResponse("ok"))

    # Ejecuta
    reply = service.get_reply(user_id=1, query="hola")

    # Asegura que se llamó al modelo
    service.model.generate_content.assert_called_once()
    full_prompt = service.model.generate_content.call_args[0][0]

    # La regla debe aparecer exactamente una vez
    assert full_prompt.count("NUNCA diagnostiques") == 1, full_prompt
    assert isinstance(reply, str) and len(reply) > 0