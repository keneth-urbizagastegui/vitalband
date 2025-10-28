# backend/app/repository/patients_repository.py

from typing import List, Optional, Dict, Any # Añadir Dict, Any
from ..extensions import db
from ..model.models import Patient

class PatientsRepository:
    @staticmethod
    def list() -> List[Patient]:
        """Obtiene todos los pacientes, ordenados por ID descendente."""
        # Se puede añadir paginación aquí si es necesario
        return Patient.query.order_by(Patient.id.desc()).all()

    @staticmethod
    def get(patient_id: int) -> Optional[Patient]:
        """Obtiene un paciente por su ID primario."""
        # Usa db.session.get que es más directo para PK
        return db.session.get(Patient, patient_id)
        # Alternativa: return Patient.query.get(patient_id)

    # --- NUEVO: Buscar por User ID ---
    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Patient]:
        """Busca un paciente por su user_id."""
        return Patient.query.filter_by(user_id=user_id).first()

    @staticmethod
    def create(first_name: str, last_name: str, email: Optional[str] = None,
               phone: Optional[str] = None, birthdate=None, sex: str = "unknown",
               height_cm=None, weight_kg=None, user_id: Optional[int] = None) -> Patient:
        """Crea y guarda un nuevo registro de paciente."""
        # La validación de user_id duplicado o email duplicado se maneja mejor en el servicio
        # o se captura la excepción de la base de datos.
        p = Patient(
            user_id=user_id, # Asume que user_id es válido y existe
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
        db.session.commit() # Guarda los cambios en la BD
        db.session.refresh(p) # Refresca el objeto 'p' con datos de la BD (como el ID asignado)
        return p

    # --- NUEVO: Actualizar Paciente ---
    @staticmethod
    def update(patient: Patient, data: Dict[str, Any]) -> Patient:
        """Actualiza los campos de un objeto Patient existente con los datos proporcionados."""
        # Itera sobre los datos recibidos (ya validados por el schema en el controller/service)
        for key, value in data.items():
            # Verifica si el atributo existe en el modelo Patient antes de asignarlo
            if hasattr(patient, key):
                setattr(patient, key, value)
            # else: Manejar campos inesperados si es necesario (ej. loggear advertencia)

        # No es necesario db.session.add(patient) porque el objeto ya está en la sesión
        db.session.commit() # Guarda los cambios en la BD
        db.session.refresh(patient) # Refresca el objeto por si hubo triggers o cambios en BD
        return patient

    # --- NUEVO: Eliminar Paciente ---
    @staticmethod
    def delete(patient: Patient) -> bool:
        """Elimina un registro de paciente de la base de datos."""
        try:
            db.session.delete(patient)
            db.session.commit() # Confirma la eliminación
            return True
        except Exception as e:
            # Loggear el error 'e' sería ideal
            db.session.rollback() # Deshace la transacción en caso de error
            return False