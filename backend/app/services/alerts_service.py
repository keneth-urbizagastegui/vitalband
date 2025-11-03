# backend/app/services/alerts_service.py

import logging
from typing import List, Optional
from datetime import datetime, timezone # Necesario para acknowledge
from ..repository.alerts_repository import AlertsRepository
from ..model.models import Alert
# Importa db si necesitas manejar la sesión directamente
from ..extensions import db

logger = logging.getLogger(__name__)

class AlertsService:
    def __init__(self, repo: AlertsRepository | None = None):
        self.repo = repo or AlertsRepository()

    def list_alerts_for_patient(self, patient_id: int, limit: int = 500) -> List[Alert]:
        """Lista las alertas para un paciente."""
        try:
            return self.repo.list_by_patient(patient_id, limit=limit)
        except Exception as e:
            logger.error(f"Error al listar alertas para paciente {patient_id}: {e}")
            return []

    # --- NUEVO: Obtener una alerta por ID ---
    def get(self, alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta específica por su ID."""
        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.get_by_id(alert_id) # Llama al repositorio real
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
            logger.error(f"Error al obtener alerta {alert_id}: {e}")
            return None

# --- NUEVO: Marcar alerta como reconocida ---
    def acknowledge(self, alert_id: int, user_id: int, notes: Optional[str] = None) -> Optional[Alert]:
        """Marca una alerta como reconocida por un usuario."""
        alert = self.get(alert_id) # Llama a la función 'get' que acabamos de arreglar
        if not alert:
            logger.warning(f"Intento de reconocer alerta no existente (ID: {alert_id})")
            return None # No encontrada

        if alert.acknowledged_by is not None:
             logger.warning(f"Intento de reconocer alerta {alert_id} que ya fue reconocida por user {alert.acknowledged_by}")
             return alert # Ya está reconocida

        try:
            now_utc = datetime.now(timezone.utc)
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            # Llama al repositorio real para guardar en BD
            return self.repo.acknowledge(alert, user_id, now_utc, notes) 
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
             logger.error(f"Error al reconocer alerta {alert_id} por usuario {user_id}: {e}")
             db.session.rollback()
             return None # O relanza
    
    # --- NUEVO: Listar alertas pendientes para el dashboard de admin ---
    def list_pending_alerts(self, limit: int = 50) -> List[Alert]:
        """Lista las alertas pendientes más recientes de todos los pacientes."""
        try:
            # Llama al nuevo método del repositorio
            return self.repo.list_pending(limit=limit)
        except Exception as e:
            logger.error(f"Error al listar alertas pendientes: {e}")
            return []

    # --- NUEVO: Listar alertas pendientes por paciente ---
    def list_pending_for_patient(self, patient_id: int, limit: int = 5) -> List[Alert]:
        """Lista las alertas pendientes (no reconocidas) para un paciente específico."""
        try:
            return self.repo.list_pending_for_patient(patient_id, limit=limit)
        except Exception as e:
            logger.error(f"Error al listar alertas pendientes para paciente {patient_id}: {e}")
            return []

    # --- NUEVO (Opcional): Contar alertas ---
    # def count_recent_by_severity(self, hours: int = 24) -> Dict[str, int]:
    #     """Cuenta alertas recientes agrupadas por severidad."""
    #     # Necesitarías un método en el repositorio
    #     # return self.repo.count_recent_by_severity(hours=hours)
    #     logger.debug("TODO: Implementar AlertsService.count_recent_by_severity()")
    #     return {"low": 0, "moderate": 0, "high": 0, "critical": 0} # Placeholder