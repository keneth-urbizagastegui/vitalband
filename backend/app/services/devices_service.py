from typing import Optional, List
from ..repository.devices_repository import DevicesRepository
from ..model.models import Device

class DevicesService:
    def __init__(self, repo: DevicesRepository | None = None):
        self.repo = repo or DevicesRepository()

    def get_by_id(self, device_id: int) -> Optional[Device]:
        return self.repo.get_by_id(device_id)

    def register_if_missing(self, serial: str, model: str, patient_id: int | None = None) -> Device:
        device = self.repo.get_by_serial(serial)
        return device or self.repo.create(serial=serial, model=model, patient_id=patient_id)

    def list_by_patient(self, patient_id: int) -> List[Device]:
        return self.repo.list_by_patient(patient_id)

    def assign_to_patient(self, device_id: int, patient_id: int | None) -> Optional[Device]:
        return self.repo.assign_to_patient(device_id, patient_id)
