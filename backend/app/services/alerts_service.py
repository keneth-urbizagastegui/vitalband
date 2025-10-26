from ..repository.alerts_repository import AlertsRepository

class AlertsService:
    def __init__(self, repo: AlertsRepository | None = None):
        self.repo = repo or AlertsRepository()

    def list_alerts_for_patient(self, patient_id: int):
        return self.repo.list_by_patient(patient_id)
