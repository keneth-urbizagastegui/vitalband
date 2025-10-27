from typing import Optional, List
from ..extensions import db
from ..model.models import Device

class DevicesRepository:
    @staticmethod
    def get_by_id(device_id: int) -> Optional[Device]:
        # SQLAlchemy 2.x: usar Session.get en lugar de Query.get (deprecado)
        return db.session.get(Device, device_id)

    @staticmethod
    def get_by_serial(serial: str) -> Optional[Device]:
        return Device.query.filter_by(serial=serial).first()

    @staticmethod
    def list_by_patient(patient_id: int) -> List[Device]:
        return (
            Device.query.filter_by(patient_id=patient_id)
            .order_by(Device.id.desc())
            .all()
        )

    @staticmethod
    def create(serial: str, model: str, patient_id: Optional[int] = None, status: str = "new") -> Device:
        d = Device(serial=serial, model=model, patient_id=patient_id, status=status)
        db.session.add(d)
        db.session.commit()
        db.session.refresh(d)
        return d

    @staticmethod
    def assign_to_patient(device_id: int, patient_id: Optional[int]) -> Optional[Device]:
        d = db.session.get(Device, device_id)  # ← reemplaza Query.get()
        if not d:
            return None
        d.patient_id = patient_id  # puede ser None para desasignar
        db.session.commit()
        db.session.refresh(d)
        return d
