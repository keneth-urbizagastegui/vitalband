from datetime import datetime
from typing import List, Optional
from ..repository.metrics_repository import MetricsRepository
from ..model.models import Reading

class MetricsService:
    def __init__(self, repo: MetricsRepository | None = None):
        self.repo = repo or MetricsRepository()

    def last_24h_for_device(self, device_id: int) -> List[Reading]:
        return self.repo.last_24h(device_id)

    def list_range(self, device_id: int,
                   dt_from: Optional[datetime] = None,
                   dt_to: Optional[datetime] = None,
                   limit: int = 1000) -> List[Reading]:
        return self.repo.list_range(device_id, dt_from, dt_to, limit)
