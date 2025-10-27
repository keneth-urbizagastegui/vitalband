from typing import Optional
from ..extensions import db
from ..model.models import Threshold

class ThresholdsRepository:
    @staticmethod
    def upsert(patient_id: Optional[int], metric: str, min_value=None, max_value=None) -> Threshold:
        t = Threshold.query.filter_by(patient_id=patient_id, metric=metric).first()
        if not t:
            t = Threshold(patient_id=patient_id, metric=metric)
            db.session.add(t)
        t.min_value = min_value
        t.max_value = max_value
        db.session.commit()
        db.session.refresh(t)
        return t

    @staticmethod
    def get(patient_id: Optional[int], metric: str) -> Optional[Threshold]:
        return Threshold.query.filter_by(patient_id=patient_id, metric=metric).first()
