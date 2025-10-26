from ..extensions import db
from ..model.models import Device

class DevicesRepository:
    def get_by_serial(self, serial: str) -> Device | None:
        return Device.query.filter_by(serial=serial).first()

    def create(self, serial: str, patient_id: int | None = None) -> Device:
        d = Device(serial=serial, patient_id=patient_id)
        db.session.add(d)
        db.session.commit()
        return d
