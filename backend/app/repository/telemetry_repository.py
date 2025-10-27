from datetime import datetime
from typing import List, Optional
from ..extensions import db
from ..model.models import DeviceTelemetry

class TelemetryRepository:
    @staticmethod
    def create(device_id: int, payload: dict) -> DeviceTelemetry:
        tel = DeviceTelemetry(device_id=device_id, **payload)
        db.session.add(tel)
        db.session.commit()
        db.session.refresh(tel)
        return tel

    @staticmethod
    def list_by_device(device_id: int,
                       dt_from: Optional[datetime] = None,
                       dt_to: Optional[datetime] = None,
                       limit: int = 1000) -> List[DeviceTelemetry]:
        q = DeviceTelemetry.query.filter_by(device_id=device_id)
        if dt_from:
            q = q.filter(DeviceTelemetry.ts >= dt_from)
        if dt_to:
            q = q.filter(DeviceTelemetry.ts <= dt_to)
        return q.order_by(DeviceTelemetry.ts.desc()).limit(limit).all()
