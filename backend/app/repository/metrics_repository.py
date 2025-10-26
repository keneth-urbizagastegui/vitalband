from datetime import datetime, timedelta
from ..model.models import Metric

class MetricsRepository:
    def last_24h(self, device_id: int) -> list[Metric]:
        since = datetime.utcnow() - timedelta(hours=24)
        return Metric.query.filter(Metric.device_id == device_id, Metric.ts >= since).all()
