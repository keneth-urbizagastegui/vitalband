from datetime import datetime
from typing import Optional, List
from flask import abort
from ..repository.telemetry_repository import TelemetryRepository
from ..repository.devices_repository import DevicesRepository
from ..model.models import DeviceTelemetry

class TelemetryService:
    def __init__(self,
                 repo: TelemetryRepository | None = None,
                 devices_repo: DevicesRepository | None = None):
        self.repo = repo or TelemetryRepository()
        self.devices_repo = devices_repo or DevicesRepository()

    def _ensure_device(self, device_id: int):
        dev = self.devices_repo.get_by_id(device_id)
        if not dev:
            abort(404, description="Device not found")
        return dev

    def create(self, device_id: int, payload: dict) -> DeviceTelemetry:
        self._ensure_device(device_id)
        return self.repo.create(device_id, payload)

    def list_by_device(self, device_id: int,
                       dt_from: Optional[datetime] = None,
                       dt_to: Optional[datetime] = None,
                       limit: int = 1000) -> List[DeviceTelemetry]:
        self._ensure_device(device_id)
        return self.repo.list_by_device(device_id, dt_from, dt_to, limit)
