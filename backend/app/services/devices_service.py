from ..repository.devices_repository import DevicesRepository

class DevicesService:
    def __init__(self, repo: DevicesRepository | None = None):
        self.repo = repo or DevicesRepository()

    def register_if_missing(self, serial: str, patient_id: int | None = None):
        device = self.repo.get_by_serial(serial)
        return device or self.repo.create(serial, patient_id)
