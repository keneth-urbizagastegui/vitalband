# backend/app/services/metrics_service.py

import logging
from datetime import datetime
from typing import List, Optional
from ..repository.metrics_repository import MetricsRepository
from ..model.models import Reading

logger = logging.getLogger(__name__)

class MetricsService:
    def __init__(self, repo: MetricsRepository | None = None):
        self.repo = repo or MetricsRepository()

    def last_24h_for_device(self, device_id: int) -> List[Reading]:
        """Obtiene las lecturas de las últimas 24h para un dispositivo."""
        try:
            return self.repo.last_24h(device_id)
        except Exception as e:
            logger.error(f"Error al obtener últimas 24h de lecturas para device {device_id}: {e}")
            return []

    def list_range(self, device_id: int,
                   dt_from: Optional[datetime] = None,
                   dt_to: Optional[datetime] = None,
                   limit: int = 1000) -> List[Reading]:
        """Obtiene lecturas para un dispositivo en un rango de fechas."""
        try:
            return self.repo.list_range(device_id, dt_from, dt_to, limit)
        except Exception as e:
            logger.error(f"Error al obtener rango de lecturas para device {device_id}: {e}")
            return []

    # --- NUEVO: Obtener la última lectura ---
    def get_latest_reading(self, device_id: int) -> Optional[Reading]:
        """Obtiene la lectura más reciente registrada para un dispositivo."""
        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.get_latest(device_id) # Llama al método correcto del repo
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
            logger.error(f"Error al obtener la última lectura para device {device_id}: {e}")
            return None