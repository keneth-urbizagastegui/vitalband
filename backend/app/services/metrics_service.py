from ..repository.metrics_repository import MetricsRepository

class MetricsService:
    def __init__(self, repo: MetricsRepository | None = None):
        self.repo = repo or MetricsRepository()

    def last_24h_for_device(self, device_id: int):
        return self.repo.last_24h(device_id)
