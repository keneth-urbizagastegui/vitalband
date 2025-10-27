from typing import List, Optional
from ..extensions import db
from ..model.models import Patient

class PatientsRepository:
    @staticmethod
    def list() -> List[Patient]:
        return Patient.query.order_by(Patient.id.desc()).all()

    @staticmethod
    def get(patient_id: int) -> Optional[Patient]:
        return Patient.query.get(patient_id)

    @staticmethod
    def create(first_name: str, last_name: str, email: Optional[str] = None,
               phone: Optional[str] = None, birthdate=None, sex: str = "unknown",
               height_cm=None, weight_kg=None, user_id: Optional[int] = None) -> Patient:
        p = Patient(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            birthdate=birthdate,
            sex=sex,
            height_cm=height_cm,
            weight_kg=weight_kg
        )
        db.session.add(p)
        db.session.commit()
        db.session.refresh(p)
        return p
