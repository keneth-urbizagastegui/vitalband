# backend/app/services/patients_service.py

import logging # Para logging
from typing import List, Optional, Dict, Any # Añadir Dict, Any
from ..repository.patients_repository import PatientsRepository
from ..model.models import Patient
# Importa db si necesitas manejar la sesión directamente (ej. para commit/rollback en update/delete)
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

    # --- NUEVO: Obtener paciente por User ID ---
    def get_by_user_id(self, user_id: int) -> Optional[Patient]:
        """Obtiene el perfil de paciente asociado a un User ID."""
        # Necesitas añadir el método `get_by_user_id` al PatientsRepository
        try:
            # return self.repo.get_by_user_id(user_id) # Descomenta cuando lo implementes
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar PatientsRepository.get_by_user_id({user_id})")
            # Simula encontrar al paciente si user_id es 1
            if user_id == 1:
                 # Necesita devolver un objeto Patient real si existe en la BD para pruebas
                 return self.repo.get(1) # Asume que el paciente con ID 1 existe
            return None
            # --- Fin Placeholder ---
        except Exception as e:
            logger.error(f"Error buscando paciente por user_id {user_id}: {e}")
            return None

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
        # Podrías añadir validaciones aquí si fueran necesarias,
        # ej. verificar si el user_id ya está asociado a otro paciente.
        if user_id is None:
             # Decide tu política: ¿Crear paciente sin usuario asociado? ¿Requerirlo?
             # Por ahora, lanzamos un error si no viene user_id, ya que la FK es NOT NULL.
             logger.error("Intento de crear paciente sin user_id.")
             raise ValueError("Se requiere user_id para crear un paciente.")

        # Verificar si el user_id ya tiene un paciente (si la relación debe ser estrictamente 1:1)
        # existing_patient = self.get_by_user_id(user_id)
        # if existing_patient:
        #      logger.warning(f"Intento de crear paciente duplicado para user_id {user_id}")
        #      raise ValueError(f"El usuario {user_id} ya tiene un perfil de paciente asociado.")

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
        except Exception as e: # Captura errores del repositorio (ej. email duplicado en patients)
             logger.error(f"Error en repositorio al crear paciente para user_id {user_id}: {e}")
             # Relanza una excepción más específica o maneja el error
             raise e # O convierte a una excepción personalizada

    # --- NUEVO: Actualizar paciente ---
    def update(self, patient_id: int, data: Dict[str, Any]) -> Optional[Patient]:
        """Actualiza los datos de un paciente existente."""
        patient = self.repo.get(patient_id)
        if not patient:
            return None # O lanza NotFoundError

        # Necesitas añadir el método `update` al PatientsRepository
        try:
            # updated_patient = self.repo.update(patient, data) # El repo aplica los cambios y hace commit
            # return updated_patient
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar PatientsRepository.update({patient_id}, {data})")
            # Simula la actualización modificando el objeto localmente (no guarda en DB)
            for key, value in data.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            # ¡Falta el db.session.commit() que debería estar en el repo!
            return patient # Devuelve el objeto modificado localmente
            # --- Fin Placeholder ---
        except Exception as e:
            logger.error(f"Error al actualizar paciente {patient_id}: {e}")
            db.session.rollback() # Asegura rollback si el commit falla en el repo
            return None # O relanza

    # --- NUEVO: Eliminar paciente ---
    def delete(self, patient_id: int) -> bool:
        """Elimina un paciente."""
        patient = self.repo.get(patient_id)
        if not patient:
            return False # No encontrado

        # Necesitas añadir el método `delete` al PatientsRepository
        try:
            # return self.repo.delete(patient) # El repo hace db.session.delete() y commit()
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar PatientsRepository.delete({patient_id})")
            # ¡Falta el db.session.delete() y commit() que debería estar en el repo!
            return True # Simula éxito
            # --- Fin Placeholder ---
        except Exception as e:
            logger.error(f"Error al eliminar paciente {patient_id}: {e}")
            db.session.rollback() # Asegura rollback
            return False

    # --- NUEVO (Opcional): Contar pacientes ---
    # def count_active(self) -> int:
    #     """Cuenta pacientes activos (ej. si tuvieran un estado)."""
    #     # Necesitarías un método en el repositorio
    #     # return self.repo.count_active()
    #     logger.debug("TODO: Implementar PatientsService.count_active()")
    #     return 0 # Placeholder