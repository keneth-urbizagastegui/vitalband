# backend/app/controller/chatbot_controller.py

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from ..services.chatbot_service import ChatbotService
from ..model.dto.request_schemas import ChatbotQueryRequest

# Define el Blueprint
chatbot_bp = Blueprint("chatbot", __name__)

# Instancia del servicio real de chatbot
_chatbot_service = ChatbotService()
_query_in = ChatbotQueryRequest()

logger = logging.getLogger(__name__)


@chatbot_bp.post("/query")
@jwt_required()
def handle_chatbot_query():
    """Recibe una consulta del usuario y devuelve la respuesta del chatbot (Gemini)."""
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    # Validación con Marshmallow
    try:
        data = _query_in.load(payload)
    except ValidationError as err:
        logger.warning(f"Consulta de chatbot inválida (usuario {user_id}): {err.messages}")
        return {"messages": err.messages}, 400

    message = data["message"]
    logger.info(f"Usuario {user_id} consultó al chatbot: '{message}'")

    # Llama al servicio real de IA
    reply_text = _chatbot_service.get_reply(user_id=user_id, query=message)

    return jsonify({"reply": reply_text}), 200


@chatbot_bp.get("/debug-context")
@jwt_required()
def debug_context():
    """Devuelve el contexto del paciente asociado al usuario autenticado, para depuración."""
    user_id = get_jwt_identity()
    logger.info(f"Usuario {user_id} solicitó contexto de depuración del chatbot")

    ctx = _chatbot_service.get_context_for_user(user_id)
    return jsonify(ctx), 200