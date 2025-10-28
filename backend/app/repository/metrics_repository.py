# backend/app/repository/metrics_repository.py

from datetime import datetime, timedelta, timezone
from typing import List, Optional
# Importa el modelo Reading
from ..model.models import Reading
# Importa db si necesitas la sesión directamente (aunque query suele ser suficiente aquí)
# from ..extensions import db

class MetricsRepository:
    """Mantiene el nombre del archivo para compatibilidad, pero trabaja con Reading."""
    @staticmethod
    def last_24h(device_id: int) -> List[Reading]:
        """Obtiene todas las lecturas de un dispositivo en las últimas 24 horas."""
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        return (Reading.query
                .filter(Reading.device_id == device_id, Reading.ts >= since)
                .order_by(Reading.ts.desc())
                .all())

    @staticmethod
    def list_range(device_id: int, dt_from: Optional[datetime] = None,
                   dt_to: Optional[datetime] = None, limit: int = 1000) -> List[Reading]:
        """Obtiene lecturas para un dispositivo filtrando por ID, rango de fechas y límite."""
        q = Reading.query.filter(Reading.device_id == device_id)
        if dt_from:
            # Asegúrate que dt_from sea timezone-aware si tus timestamps lo son
            q = q.filter(Reading.ts >= dt_from)
        if dt_to:
            # Asegúrate que dt_to sea timezone-aware
            q = q.filter(Reading.ts <= dt_to)
        # Ordena descendente por timestamp y aplica el límite
        return q.order_by(Reading.ts.desc()).limit(limit).all()

    # --- NUEVO: Obtener la última lectura ---
    @staticmethod
    def get_latest(device_id: int) -> Optional[Reading]:
        """
        Obtiene la lectura más reciente (última por timestamp)
        para un dispositivo específico.
        """
        return (Reading.query
                .filter(Reading.device_id == device_id)
                .order_by(Reading.ts.desc()) # Ordena por fecha, la más nueva primero
                .first()) # Toma solo el primer resultado (el más reciente)