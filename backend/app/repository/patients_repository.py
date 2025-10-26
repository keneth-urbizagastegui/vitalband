from ..extensions import db
from ..model.models import Patient

class PatientsRepository:
    def list(self) -> list[Patient]:
        return Patient.query.order_by(Patient.id.desc()).all()

    def get(self, patient_id: int) -> Patient | None:
        return Patient.query.get(patient_id)

    def create(self, full_name: str, email: str | None = None) -> Patient:
        p = Patient(full_name=full_name, email=email)
        db.session.add(p)
        db.session.commit()
        return p
