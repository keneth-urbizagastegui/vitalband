# backend/app/services/chatbot_service.py

import logging
import os
import google.generativeai as genai
from ..services.patients_service import PatientsService
from ..services.metrics_service import MetricsService
from ..services.alerts_service import AlertsService
from ..services.devices_service import DevicesService
from ..services.thresholds_service import ThresholdsService
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None  # type: ignore

logger = logging.getLogger(__name__)


class ChatbotService:
    def __init__(self):
        """Inicializa el servicio del chatbot con Google Gemini."""
        self.model = None
        self.model_name = None  # nombre del modelo configurado
        self.system_prompt = (
            """
Eres VitalBot, un asistente de IA informativo para la plataforma de monitoreo de salud VitalBand.
Tu tono es amigable, empático y profesional.

REGLA MÁS IMPORTANTE: NO ERES UN MÉDICO. NUNCA DEBES DAR CONSEJOS MÉDICOS, DIAGNÓSTICOS O INTERPRETACIONES MÉDICAS.
- SIEMPRE que un usuario te pregunte algo médico (ej. "¿es grave mi ritmo cardíaco?", "¿qué medicina tomo?"), DEBES responder amablemente que no puedes dar consejos médicos y que debe consultar a su doctor.
- SÍ PUEDES explicar qué es una métrica de forma general (ej. "SpO2 es la saturación de oxígeno...").
- SÍ PUEDES responder preguntas sobre cómo usar la app VitalBand.
- Responde en español de forma clara y breve.
- Al usar el contexto del paciente, SÓLO debes informar al paciente sobre sus datos (ej. 'Tu última métrica fue X') o sus umbrales (ej. 'Tu rango configurado es Y-Z'). NUNCA diagnostiques (ej. 'Tu ritmo es peligroso' o 'Tienes fiebre'). Refiere SIEMPRE a un médico para cualquier interpretación.
"""
        )

        try:
            # Intenta cargar variables desde backend/.env (si python-dotenv está disponible)
            if load_dotenv:
                env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
                load_dotenv(env_path)

            # Lee la clave GOOGLE_API_KEY
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY no está configurada. El chatbot de IA no funcionará.")
                return

            # Configura la API
            genai.configure(api_key=api_key)

            # Permitir configurar el modelo por entorno; para maximizar compatibilidad con API estable usar nombres 'models/...'
            # Valor por defecto apuntando a un alias generalmente disponible en v1 estable
            raw_model_env = os.getenv("AI_MODEL")
            default_model = "models/gemini-flash-latest"

            # Normaliza el nombre: si el valor no incluye el prefijo 'models/', lo intentamos con y sin prefijo
            candidates = []
            if raw_model_env:
                if raw_model_env.startswith("models/"):
                    candidates = [raw_model_env]
                else:
                    candidates = [f"models/{raw_model_env}", raw_model_env]
            else:
                candidates = [default_model]

            last_error = None
            for cand in candidates:
                try:
                    self.model = genai.GenerativeModel(model_name=cand, system_instruction=self.system_prompt)
                    self.model_name = cand
                    logger.info(f"ChatbotService inicializado con Google Gemini API (modelo='{self.model_name}').")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"No se pudo inicializar el modelo '{cand}'. Error: {e}")

            # Si ninguno de los candidatos funcionó, intentar con el fallback estable
            if self.model is None:
                try:
                    self.model = genai.GenerativeModel(model_name=default_model, system_instruction=self.system_prompt)
                    self.model_name = default_model
                    logger.info(f"ChatbotService inicializado con modelo por defecto '{self.model_name}'.")
                except Exception as e:
                    logger.error(f"Error al inicializar cualquier modelo de Gemini. Último error: {last_error or e}")

            # Inicializa servicios para recuperar contexto del paciente
            self.patients_service = PatientsService()
            self.metrics_service = MetricsService()
            self.alerts_service = AlertsService()
            self.devices_service = DevicesService()
            self.thresholds_service = ThresholdsService()
        except Exception as e:
            logger.error(f"Error al inicializar Google Gemini: {e}")

    def get_reply(self, user_id: int, query: str) -> str:
        """Procesa la consulta del usuario y devuelve la respuesta del chatbot con contexto del paciente."""
        logger.debug(f"Procesando consulta de IA para user {user_id}: '{query}'")

        if not self.model:
            logger.error("Intento de usar chatbot sin un modelo de IA configurado.")
            return "Lo siento, el servicio de chatbot no está disponible en este momento."

        # --- 1. RECUPERAR CONTEXTO (RAG) ---
        try:
            contexto_dict = self.get_context_for_user(user_id)
        except Exception as e:
            logger.error(f"Error al recuperar contexto para user {user_id}: {e}")
            contexto_dict = {}

        # Construye un string legible del contexto
        contexto_del_paciente_parts = []
        contexto_del_paciente_parts.append("--- Contexto del Paciente (Solo para tu información) ---")
        try:
            nombre = (contexto_dict.get("patient", {}) or {}).get("full_name")
            if nombre:
                contexto_del_paciente_parts.append(f"Nombre: {nombre}")

            latest = (contexto_dict.get("latest_reading") or None)
            if latest:
                hr = latest.get("heart_rate_bpm")
                spo2 = latest.get("spo2_pct")
                temp = latest.get("temp_c")
                contexto_del_paciente_parts.append(
                    f"Última Métrica: HR={hr} bpm, SpO2={spo2}%, Temp={temp}°C."
                )

            pend = contexto_dict.get("pending_alerts", []) or []
            if pend:
                contexto_del_paciente_parts.append(
                    f"Alertas Pendientes: {len(pend)} (ej. {pend[0].get('type')} - {pend[0].get('severity')})"
                )
            else:
                contexto_del_paciente_parts.append("Alertas Pendientes: 0")

            thr = contexto_dict.get("thresholds") or {}
            if thr:
                hr_min = (thr.get("heart_rate", {}) or {}).get("min_value")
                hr_max = (thr.get("heart_rate", {}) or {}).get("max_value")
                spo2_min = (thr.get("spo2", {}) or {}).get("min_value")
                spo2_max = (thr.get("spo2", {}) or {}).get("max_value")
                temp_min = (thr.get("temperature", {}) or {}).get("min_value")
                temp_max = (thr.get("temperature", {}) or {}).get("max_value")
                contexto_del_paciente_parts.append(
                    f"Umbrales: HR={hr_min}-{hr_max} bpm, SpO2={spo2_min}-{spo2_max} %, Temp={temp_min}-{temp_max} °C"
                )
        except Exception:
            # En caso de problemas de formateo, continuamos sin añadir más datos
            pass

        contexto_del_paciente_parts.append("--- Fin del Contexto ---")
        contexto_del_paciente = "\n".join(contexto_del_paciente_parts)

        # --- 2. GENERAR RESPUESTA ---
        try:
            # Inyectamos el contexto entre el system_prompt y la consulta
            full_prompt = f"{self.system_prompt}\n{contexto_del_paciente}\n\nUsuario: {query}\nAsistente:"

            response = self.model.generate_content(full_prompt)

            if getattr(response, "text", None):
                logger.info(f"Respuesta de Gemini generada con contexto para user {user_id}")
                return response.text
            else:
                logger.warning(f"Gemini no devolvió texto para la consulta: {query}")
                return "No pude procesar esa respuesta. Inténtalo de nuevo."
        except Exception as e:
            logger.error(f"Error interactuando con la IA para user {user_id}: {e}", exc_info=True)
            return "Lo siento, tuve un problema al generar la respuesta. Por favor, inténtalo de nuevo más tarde."

    def get_context_for_user(self, user_id: int) -> dict:
        """Recupera el contexto del paciente asociado al user_id para depuración y RAG.

        Estructura devuelta:
        {
          "patient": {"id": int, "full_name": str} | None,
          "device": {"id": int, "model": str, "serial": str} | None,
          "latest_reading": {"id": int, "ts": str, "heart_rate_bpm": int, "spo2_pct": int, "temp_c": float} | None,
          "pending_alerts": [{"id": int, "ts": str, "type": str, "severity": str, "message": str}],
          "thresholds": {
             "heart_rate": {"min_value": float | None, "max_value": float | None},
             "spo2": {"min_value": float | None, "max_value": float | None},
             "temperature": {"min_value": float | None, "max_value": float | None}
          }
        }
        """
        ctx: dict = {
            "patient": None,
            "device": None,
            "latest_reading": None,
            "pending_alerts": [],
            "thresholds": {}
        }

        try:
            patient = self.patients_service.get_by_user_id(user_id)
            if patient:
                ctx["patient"] = {
                    "id": patient.id,
                    "full_name": patient.full_name,
                }

                devices = self.devices_service.list_by_patient(patient.id)
                if devices:
                    dev = devices[0]
                    ctx["device"] = {
                        "id": dev.id,
                        "model": getattr(dev, "model", None),
                        "serial": getattr(dev, "serial", None),
                    }

                    latest = self.metrics_service.get_latest_reading(dev.id)
                    if latest:
                        # Convierte tipos a JSON-friendly
                        temp_c = None
                        try:
                            temp_c = float(latest.temp_c) if latest.temp_c is not None else None
                        except Exception:
                            temp_c = None

                        ts_iso = None
                        try:
                            ts_iso = latest.ts.isoformat() if latest.ts else None
                        except Exception:
                            ts_iso = None

                        ctx["latest_reading"] = {
                            "id": latest.id,
                            "ts": ts_iso,
                            "heart_rate_bpm": latest.heart_rate_bpm,
                            "spo2_pct": latest.spo2_pct,
                            "temp_c": temp_c,
                        }

                pending = self.alerts_service.list_pending_for_patient(patient.id, limit=5)
                ctx["pending_alerts"] = [
                    {
                        "id": a.id,
                        "ts": (a.ts.isoformat() if getattr(a, "ts", None) else None),
                        "type": getattr(a, "type", None),
                        "severity": getattr(a, "severity", None),
                        "message": getattr(a, "message", None),
                    }
                    for a in (pending or [])
                ]

                # Umbrales del paciente (con fallback a global si aplica)
                try:
                    th_hr = self.thresholds_service.get_thresholds(patient.id, "heart_rate")
                    th_spo2 = self.thresholds_service.get_thresholds(patient.id, "spo2")
                    th_temp = self.thresholds_service.get_thresholds(patient.id, "temperature")

                    def d_to_float(d):
                        try:
                            return float(d) if d is not None else None
                        except Exception:
                            return None

                    ctx["thresholds"] = {
                        "heart_rate": {
                            "min_value": d_to_float(getattr(th_hr, "min_value", None)),
                            "max_value": d_to_float(getattr(th_hr, "max_value", None)),
                        },
                        "spo2": {
                            "min_value": d_to_float(getattr(th_spo2, "min_value", None)),
                            "max_value": d_to_float(getattr(th_spo2, "max_value", None)),
                        },
                        "temperature": {
                            "min_value": d_to_float(getattr(th_temp, "min_value", None)),
                            "max_value": d_to_float(getattr(th_temp, "max_value", None)),
                        },
                    }
                except Exception as e:
                    logger.warning(f"No se pudieron recuperar umbrales para patient_id={patient.id}: {e}")
        except Exception as e:
            logger.error(f"Error al recuperar contexto para user {user_id}: {e}", exc_info=True)

        return ctx