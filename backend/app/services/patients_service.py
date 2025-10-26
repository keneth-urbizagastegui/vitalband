from ..repository.patients_repository import PatientsRepository

class PatientsService:
    def __init__(self, repo: PatientsRepository | None = None):
        self.repo = repo or PatientsRepository()

    def list_patients(self):
        return self.repo.list()

    def create_patient(self, full_name: str, email: str | None = None):
        return self.repo.create(full_name=full_name, email=email)
