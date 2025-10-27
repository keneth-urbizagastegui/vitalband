from datetime import datetime, timedelta, timezone
from typing import List, Optional
from ..model.models import Reading

class MetricsRepository:
    """Mantiene el nombre del archivo para compatibilidad, pero trabaja con Reading."""
    @staticmethod
    def last_24h(device_id: int) -> List[Reading]:
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        return (Reading.query
                .filter(Reading.device_id == device_id, Reading.ts >= since)
                .order_by(Reading.ts.desc())
                .all())

    @staticmethod
    def list_range(device_id: int, dt_from: Optional[datetime] = None,
                   dt_to: Optional[datetime] = None, limit: int = 1000) -> List[Reading]:
        q = Reading.query.filter(Reading.device_id == device_id)
        if dt_from:
            q = q.filter(Reading.ts >= dt_from)
        if dt_to:
            q = q.filter(Reading.ts <= dt_to)
        return q.order_by(Reading.ts.desc()).limit(limit).all()
