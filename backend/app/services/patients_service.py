# backend/app/services/patients_service.py

import logging
from typing import List, Optional, Dict, Any
from ..repository.patients_repository import PatientsRepository
from ..model.models import Patient
from ..extensions import db

logger = logging.getLogger(__name__)

class PatientsService:
    def __init__(self, repo: PatientsRepository | None = None):
        self.repo = repo or PatientsRepository()

    def list_patients(self) -> List[Patient]:
        """Lista todos los pacientes."""
        return self.repo.list()

    def get(self, patient_id: int) -> Optional[Patient]:
        """Obtiene un paciente por su ID."""
        return self.repo.get(patient_id)

    # --- MÉTODO ACTUALIZADO ---
    def get_by_user_id(self, user_id: int) -> Optional[Patient]:
        """Obtiene el perfil de paciente asociado a un User ID."""
        # Llama directamente al método del repositorio que acabamos de añadir.
        try:
            return self.repo.get_by_user_id(user_id) # Usa el repo
        except Exception as e:
            logger.error(f"Error buscando paciente por user_id {user_id}: {e}")
            return None
    # --- FIN MÉTODO ACTUALIZADO ---

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
        """Crea un nuevo paciente."""
        if user_id is None:
             logger.error("Intento de crear paciente sin user_id.")
             raise ValueError("Se requiere user_id para crear un paciente.")

        # Opcional: Verificar si el user_id ya tiene un paciente
        existing_patient = self.get_by_user_id(user_id)
        if existing_patient:
             logger.warning(f"Intento de crear paciente duplicado para user_id {user_id}")
             raise ValueError(f"El usuario {user_id} ya tiene un perfil de paciente asociado.")

        try:
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
        except Exception as e:
             logger.error(f"Error en repositorio al crear paciente para user_id {user_id}: {e}")
             raise e

    def update(self, patient_id: int, data: Dict[str, Any]) -> Optional[Patient]:
        """Actualiza los datos de un paciente existente."""
        patient = self.repo.get(patient_id)
        if not patient:
            return None

        try:
            # Llama al método update del repositorio
            return self.repo.update(patient, data) # Usa el repo
        except Exception as e:
            logger.error(f"Error al actualizar paciente {patient_id}: {e}")
            db.session.rollback()
            return None

    def delete(self, patient_id: int) -> bool:
        """Elimina un paciente."""
        patient = self.repo.get(patient_id)
        if not patient:
            return False

        try:
            # Llama al método delete del repositorio
            return self.repo.delete(patient) # Usa el repo
        except Exception as e:
            logger.error(f"Error al eliminar paciente {patient_id}: {e}")
            db.session.rollback()
            return False