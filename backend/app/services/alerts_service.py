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
        # Necesitas añadir `get_by_id` al AlertsRepository
        try:
            # return self.repo.get_by_id(alert_id) # Descomenta cuando lo implementes
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar AlertsRepository.get_by_id({alert_id})")
            # Simula encontrar la alerta si el ID es bajo (ej. < 10)
            if alert_id < 10:
                # Intenta devolver una alerta real si existe para pruebas
                existing_alerts = self.list_alerts_for_patient(1, limit=10) # Asume paciente 1
                return next((a for a in existing_alerts if a.id == alert_id), None)
            return None
            # --- Fin Placeholder ---
        except Exception as e:
            logger.error(f"Error al obtener alerta {alert_id}: {e}")
            return None

    # --- NUEVO: Marcar alerta como reconocida ---
    def acknowledge(self, alert_id: int, user_id: int, notes: Optional[str] = None) -> Optional[Alert]:
        """Marca una alerta como reconocida por un usuario."""
        alert = self.get(alert_id) # Reutiliza el método get para encontrarla
        if not alert:
            logger.warning(f"Intento de reconocer alerta no existente (ID: {alert_id})")
            return None # No encontrada

        if alert.acknowledged_by is not None:
             logger.warning(f"Intento de reconocer alerta {alert_id} que ya fue reconocida por user {alert.acknowledged_by}")
             # Decide política: ¿Error? ¿Actualizar? ¿Ignorar? Por ahora, devolvemos la alerta como está.
             return alert # Ya está reconocida

        # Necesitas añadir `acknowledge` al AlertsRepository
        try:
            now_utc = datetime.now(timezone.utc)
            # return self.repo.acknowledge(alert, user_id, now_utc, notes) # El repo actualiza y hace commit
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar AlertsRepository.acknowledge({alert_id}, user {user_id}, timestamp={now_utc}, notes='{notes}')")
            # Simula actualización local
            alert.acknowledged_by = user_id
            alert.acknowledged_at = now_utc
            # Si hubiera un campo 'notes' en el modelo Alert, lo actualizarías aquí también
            # ¡Falta commit en repo!
            return alert # Devuelve objeto modificado localmente
            # --- Fin Placeholder ---
        except Exception as e:
             logger.error(f"Error al reconocer alerta {alert_id} por usuario {user_id}: {e}")
             db.session.rollback()
             return None # O relanza

    # --- NUEVO (Opcional): Contar alertas ---
    # def count_recent_by_severity(self, hours: int = 24) -> Dict[str, int]:
    #     """Cuenta alertas recientes agrupadas por severidad."""
    #     # Necesitarías un método en el repositorio
    #     # return self.repo.count_recent_by_severity(hours=hours)
    #     logger.debug("TODO: Implementar AlertsService.count_recent_by_severity()")
    #     return {"low": 0, "moderate": 0, "high": 0, "critical": 0} # Placeholder