# backend/app/repository/patients_repository.py

from typing import List, Optional, Dict, Any
from ..extensions import db
from ..model.models import Patient

class PatientsRepository:
    @staticmethod
    def list() -> List[Patient]:
        """Obtiene todos los pacientes, ordenados por ID descendente."""
        return Patient.query.order_by(Patient.id.desc()).all()

    @staticmethod
    def get(patient_id: int) -> Optional[Patient]:
        """Obtiene un paciente por su ID primario."""
        return db.session.get(Patient, patient_id)

    # --- MÉTODO AÑADIDO ---
    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Patient]:
        """Busca un paciente por su user_id (clave foránea única)."""
        # Como user_id es UNIQUE en la tabla patients, first() es seguro.
        return Patient.query.filter_by(user_id=user_id).first()
    # --- FIN MÉTODO AÑADIDO ---

    @staticmethod
    def create(first_name: str, last_name: str, email: Optional[str] = None,
               phone: Optional[str] = None, birthdate=None, sex: str = "unknown",
               height_cm=None, weight_kg=None, user_id: Optional[int] = None) -> Patient:
        """Crea y guarda un nuevo registro de paciente."""
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

    @staticmethod
    def update(patient: Patient, data: Dict[str, Any]) -> Patient:
        """Actualiza los campos de un objeto Patient existente con los datos proporcionados."""
        for key, value in data.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        db.session.commit()
        db.session.refresh(patient)
        return patient

    @staticmethod
    def delete(patient: Patient) -> bool:
        """Elimina un registro de paciente de la base de datos."""
        try:
            db.session.delete(patient)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False