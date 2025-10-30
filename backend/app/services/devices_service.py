# backend/app/services/devices_service.py

import logging
from typing import Optional, List, Dict, Any # Añadir Dict, Any
from ..repository.devices_repository import DevicesRepository
from ..model.models import Device
# Importa db si necesitas manejar la sesión directamente
from ..extensions import db

logger = logging.getLogger(__name__)

class DevicesService:
    def __init__(self, repo: DevicesRepository | None = None):
        self.repo = repo or DevicesRepository()

    def get_by_id(self, device_id: int) -> Optional[Device]:
        """Obtiene un dispositivo por su ID."""
        return self.repo.get_by_id(device_id)

    # --- NUEVO: Obtener dispositivo por serial (ya estaba en repo, exponerlo) ---
    def get_by_serial(self, serial: str) -> Optional[Device]:
        """Obtiene un dispositivo por su número de serie."""
        return self.repo.get_by_serial(serial)

    def register_if_missing(self, serial: str, model: str, patient_id: int | None = None) -> Device:
        """Registra un dispositivo si no existe por serial, si existe lo devuelve."""
        device = self.repo.get_by_serial(serial)
        if device:
            # Podrías decidir actualizar el 'model' o 'patient_id' si ya existe,
            # o simplemente devolverlo como está. Por ahora, lo devolvemos.
            logger.info(f"Intento de registrar dispositivo existente (serial: {serial}), devolviendo existente.")
            return device
        # Si no existe, lo crea
        try:
            # Llama al método create del repositorio
            return self.repo.create(serial=serial, model=model, patient_id=patient_id)
        except Exception as e:
             logger.error(f"Error en repositorio al crear dispositivo (serial: {serial}): {e}")
             raise e # Relanza para que el controlador maneje el error

    # --- NUEVO: Crear un dispositivo (para admin, sin chequeo 'if_missing') ---
    def create(self, serial: str, model: str, status: str = "new", patient_id: int | None = None) -> Device:
        """Crea un nuevo dispositivo (llamado por admin)."""
        # Validar si el serial ya existe ANTES de llamar al repo para dar un error más claro
        if self.repo.get_by_serial(serial):
             logger.warning(f"Intento de crear dispositivo con serial duplicado: {serial}")
             # Lanza una excepción específica o un ValueError
             raise ValueError(f"Ya existe un dispositivo con el serial {serial}.")
        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.create(serial=serial, model=model, status=status, patient_id=patient_id)
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
            logger.error(f"Error en repositorio al crear dispositivo (serial: {serial}): {e}")
            raise e

    # --- NUEVO: Listar todos los dispositivos (para admin) ---
    def list_all(self, page: int = 1, per_page: int = 100) -> List[Device]: # Añade paginación básica
        """Lista todos los dispositivos registrados."""
        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.list_all(page=page, per_page=per_page)
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
            logger.error(f"Error al listar todos los dispositivos: {e}")
            return []

    def list_by_patient(self, patient_id: int) -> List[Device]:
        """Lista los dispositivos asignados a un paciente."""
        return self.repo.list_by_patient(patient_id)

    # --- NUEVO: Obtener un dispositivo específico de un paciente (para verificación) ---
    def get_patient_device(self, patient_id: int, device_id: int) -> Optional[Device]:
        """Obtiene un dispositivo si pertenece al paciente especificado."""
        # Necesitas añadir `get_patient_device` al DevicesRepository
        try:
            # return self.repo.get_patient_device(patient_id, device_id)
            # --- Placeholder ---
            logger.debug(f"TODO: Implementar DevicesRepository.get_patient_device({patient_id}, {device_id})")
            # Simula: obtiene el device y verifica el patient_id
            device = self.repo.get_by_id(device_id)
            if device and device.patient_id == patient_id:
                return device
            return None
            # --- Fin Placeholder ---
        except Exception as e:
            logger.error(f"Error buscando dispositivo {device_id} para paciente {patient_id}: {e}")
            return None


    def assign_to_patient(self, device_id: int, patient_id: int | None) -> Optional[Device]:
        """Asigna o desasigna un dispositivo a un paciente."""
        # Lógica adicional: ¿Debería verificarse si el dispositivo ya está asignado a OTRO paciente?
        device = self.repo.get_by_id(device_id)
        if not device:
             logger.warning(f"Intento de asignar dispositivo no existente (ID: {device_id})")
             return None # O lanza NotFound

        # Opcional: Verificar si ya está asignado a otro paciente y manejarlo (ej. lanzar error)
        # if device.patient_id is not None and device.patient_id != patient_id and patient_id is not None:
        #    logger.warning(f"Dispositivo {device_id} ya asignado a paciente {device.patient_id}. No se puede reasignar directamente.")
        #    raise ValueError("El dispositivo ya está asignado a otro paciente.")

        try:
            return self.repo.assign_to_patient(device_id, patient_id)
        except Exception as e:
             logger.error(f"Error al asignar dispositivo {device_id} a paciente {patient_id}: {e}")
             db.session.rollback()
             raise e # Relanza

    # --- NUEVO: Actualizar dispositivo ---
    def update(self, device: Device, data: Dict[str, Any]) -> Optional[Device]: # Recibe el objeto
        """Actualiza datos de un dispositivo (ej. status, model)."""
        # El controlador ya verificó que el dispositivo existe
        if not device:
            return None

        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.update(device, data) # El repo aplica cambios y hace commit
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
             logger.error(f"Error al actualizar dispositivo {device.id}: {e}")
             db.session.rollback()
             return None # O relanza

# --- NUEVO: Eliminar dispositivo ---
    def delete(self, device: Device) -> bool: # Recibe el objeto
        """Elimina un dispositivo."""
        # El controlador ya verificó que el dispositivo existe
        if not device:
            return False

        try:
            # --- INICIO DEL CÓDIGO REAL (REEMPLAZA EL PLACEHOLDER) ---
            return self.repo.delete(device) # El repo hace delete y commit
            # --- FIN DEL CÓDIGO REAL ---
        except Exception as e:
            logger.error(f"Error al eliminar dispositivo {device.id}: {e}")
            db.session.rollback()
            return False

    # --- NUEVO (Opcional): Contar dispositivos ---
    # def count_active(self) -> int:
    #     """Cuenta dispositivos activos."""
    #     # Necesitarías un método en el repositorio
    #     # return self.repo.count_by_status('active')
    #     logger.debug("TODO: Implementar DevicesService.count_active()")
    #     return 0 # Placeholder