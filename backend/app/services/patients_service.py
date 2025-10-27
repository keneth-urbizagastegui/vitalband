from typing import List, Optional
from ..repository.patients_repository import PatientsRepository
from ..model.models import Patient

class PatientsService:
    def __init__(self, repo: PatientsRepository | None = None):
        self.repo = repo or PatientsRepository()

    def list_patients(self) -> List[Patient]:
        return self.repo.list()

    def get(self, patient_id: int) -> Optional[Patient]:
        return self.repo.get(patient_id)

    def create_patient(self, *,
                       first_name: str,
                       last_name: str,
                       email: str | None = None,
                       phone: str | None = None,
                       birthdate=None,
                       sex: str = "unknown",
                       height_cm=None,
                       weight_kg=None,
                       user_id: int | None = None) -> Patient:
        return self.repo.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            birthdate=birthdate,
            sex=sex,
            height_cm=height_cm,
            weight_kg=weight_kg,
            user_id=user_id,
        )
