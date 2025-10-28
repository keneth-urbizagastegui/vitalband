# backend/app/repository/devices_repository.py

from typing import Optional, List, Dict, Any # Añadir Dict, Any
from sqlalchemy import select, update as sqlalchemy_update # Para SQLAlchemy 2.0+ style (opcional)
from ..extensions import db
from ..model.models import Device

class DevicesRepository:
    @staticmethod
    def get_by_id(device_id: int) -> Optional[Device]:
        """Obtiene un dispositivo por su ID primario."""
        return db.session.get(Device, device_id)

    @staticmethod
    def get_by_serial(serial: str) -> Optional[Device]:
        """Obtiene un dispositivo por su número de serie."""
        # SQLAlchemy 1.x style
        return Device.query.filter_by(serial=serial).first()
        # SQLAlchemy 2.0+ style (alternativa)
        # stmt = select(Device).where(Device.serial == serial)
        # return db.session.scalars(stmt).first()

    # --- NUEVO: Listar Todos los Dispositivos con Paginación ---
    @staticmethod
    def list_all(page: int = 1, per_page: int = 100) -> List[Device]:
        """Lista todos los dispositivos, ordenados por ID, con paginación."""
        # SQLAlchemy 1.x style
        query = Device.query.order_by(Device.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items
        # SQLAlchemy 2.0+ style (alternativa)
        # stmt = select(Device).order_by(Device.id.desc()).limit(per_page).offset((page - 1) * per_page)
        # return list(db.session.scalars(stmt).all())

    @staticmethod
    def list_by_patient(patient_id: int) -> List[Device]:
        """Lista los dispositivos asignados a un paciente específico."""
        return (
            Device.query.filter_by(patient_id=patient_id)
            .order_by(Device.id.desc())
            .all()
        )

    # --- NUEVO: Obtener dispositivo específico de un paciente ---
    @staticmethod
    def get_patient_device(patient_id: int, device_id: int) -> Optional[Device]:
        """Obtiene un dispositivo si pertenece al paciente especificado."""
        # SQLAlchemy 1.x style
        return Device.query.filter_by(id=device_id, patient_id=patient_id).first()
        # SQLAlchemy 2.0+ style (alternativa)
        # stmt = select(Device).where(Device.id == device_id, Device.patient_id == patient_id)
        # return db.session.scalars(stmt).first()

    @staticmethod
    def create(serial: str, model: str, patient_id: Optional[int] = None, status: str = "new") -> Device:
        """Crea y guarda un nuevo registro de dispositivo."""
        # La validación de serial duplicado debe hacerse en el servicio antes de llamar aquí,
        # o capturar la IntegrityError de SQLAlchemy aquí o en el servicio.
        d = Device(serial=serial, model=model, patient_id=patient_id, status=status)
        db.session.add(d)
        db.session.commit()
        db.session.refresh(d)
        return d

    @staticmethod
    def assign_to_patient(device_id: int, patient_id: Optional[int]) -> Optional[Device]:
        """Asigna o desasigna un dispositivo actualizando su patient_id."""
        d = db.session.get(Device, device_id)
        if not d:
            return None
        d.patient_id = patient_id # Actualiza el campo
        db.session.commit() # Guarda el cambio
        db.session.refresh(d)
        return d

    # --- NUEVO: Actualizar Dispositivo ---
    @staticmethod
    def update(device: Device, data: Dict[str, Any]) -> Device:
        """Actualiza los campos permitidos de un objeto Device existente."""
        allowed_fields = ["model", "status"] # Campos que se pueden modificar
        updated = False
        for key, value in data.items():
            if key in allowed_fields and hasattr(device, key) and getattr(device, key) != value:
                setattr(device, key, value)
                updated = True

        if updated:
            db.session.commit() # Guarda solo si hubo cambios
            db.session.refresh(device)
        return device

        # Alternativa SQLAlchemy 2.0+ style (menos común para updates parciales basados en objeto):
        # if updated:
        #   update_data = {k: data[k] for k in allowed_fields if k in data}
        #   stmt = sqlalchemy_update(Device).where(Device.id == device.id).values(**update_data)
        #   db.session.execute(stmt)
        #   db.session.commit()
        #   db.session.refresh(device) # Necesario para actualizar el objeto en memoria
        # return device

    # --- NUEVO: Eliminar Dispositivo ---
    @staticmethod
    def delete(device: Device) -> bool:
        """Elimina un registro de dispositivo de la base de datos."""
        # ¡IMPORTANTE! El modelo tiene cascade="all, delete-orphan" para readings y telemetry.
        # Esto significa que al borrar el dispositivo, SQLAlchemy también borrará
        # automáticamente todos sus registros asociados en esas tablas.
        try:
            db.session.delete(device)
            db.session.commit()
            return True
        except Exception as e:
            # Loggear error 'e'
            db.session.rollback()
            return False