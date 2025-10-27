from typing import List
from ..repository.alerts_repository import AlertsRepository
from ..model.models import Alert

class AlertsService:
    def __init__(self, repo: AlertsRepository | None = None):
        self.repo = repo or AlertsRepository()

    def list_alerts_for_patient(self, patient_id: int, limit: int = 500) -> List[Alert]:
        return self.repo.list_by_patient(patient_id, limit=limit)
