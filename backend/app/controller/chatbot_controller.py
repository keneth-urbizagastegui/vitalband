# backend/app/controller/chatbot_controller.py

import logging
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

# --- Importar Servicio (a crear) ---
# Asume que tendrás un servicio que maneja la lógica del chatbot
# from ..services.chatbot_service import ChatbotService

# --- Importar Schemas (a crear) ---
# Asume schemas simples para la entrada y salida del chat
# from ..model.dto.request_schemas import ChatbotQueryRequest
# from ..model.dto.response_schemas import ChatbotResponse

# --- Define el Blueprint ---
# Usaremos /api/v1/chatbot como prefijo base
chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# --- Instancias (Placeholder) ---
# _chatbot_service = ChatbotService() # Descomenta cuando crees el servicio
# _query_in = ChatbotQueryRequest() # Descomenta cuando crees el schema
# _reply_out = ChatbotResponse() # Descomenta cuando crees el schema

logger = logging.getLogger(__name__)

@chatbot_bp.post("/query")
@jwt_required() # Requiere que el usuario esté logueado para usar el chatbot
def handle_chatbot_query():
    """Recibe una consulta del usuario y devuelve la respuesta del chatbot."""
    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    # --- Validación de Entrada (Placeholder) ---
    # try:
    #     data = _query_in.load(payload) # Valida que exista 'message'
    # except ValidationError as err:
    #     logger.warning(f"Consulta de chatbot inválida (usuario {user_id}): {err.messages}")
    #     return {"messages": err.messages}, 400
    # message = data["message"]
    # --- Fin Validación Placeholder ---

    # --- Validación Simple Temporal ---
    message = payload.get("message")
    if not message or not isinstance(message, str) or not message.strip():
        logger.warning(f"Consulta de chatbot vacía o inválida (usuario {user_id})")
        return {"message": "La consulta no puede estar vacía."}, 400
    message = message.strip()
    # --- Fin Validación Simple ---

    logger.info(f"Usuario {user_id} consultó al chatbot: '{message}'")

    # --- Llamada al Servicio (Placeholder) ---
    try:
        # Aquí llamarías a tu servicio de chatbot
        # reply_text = _chatbot_service.get_reply(user_id=user_id, query=message)

        # --- Respuesta Dummy Temporal ---
        if "hola" in message.lower():
            reply_text = f"¡Hola! Soy el asistente de VitalBand. ¿En qué puedo ayudarte hoy?"
        elif "ritmo cardiaco" in message.lower():
             reply_text = "El ritmo cardíaco normal en reposo suele estar entre 60 y 100 bpm. Si tienes preocupaciones sobre tus lecturas, consulta a un médico."
        elif "temperatura" in message.lower():
             reply_text = "Una temperatura corporal normal suele rondar los 36.5-37.5°C. La fiebre se considera generalmente por encima de 38°C."
        else:
            reply_text = "Gracias por tu consulta. Aún estoy aprendiendo a responder sobre eso. Puedes preguntarme sobre 'ritmo cardiaco' o 'temperatura'."
        # --- Fin Respuesta Dummy ---

        # --- Formateo de Salida (Placeholder) ---
        # response_data = {"reply": reply_text}
        # return _reply_out.dump(response_data), 200
        # --- Fin Formateo Placeholder ---

        # --- Salida Simple Temporal ---
        return jsonify({"reply": reply_text}), 200
        # --- Fin Salida Simple ---

    except Exception as e:
        logger.error(f"Error al procesar consulta de chatbot para usuario {user_id}: {e}", exc_info=True)
        # Podrías tener excepciones específicas del servicio de chatbot
        abort(500, description="Hubo un error al procesar tu consulta con el chatbot.")