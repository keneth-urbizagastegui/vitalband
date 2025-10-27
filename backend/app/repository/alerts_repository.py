from typing import List, Optional
from ..model.models import Alert

class AlertsRepository:
    @staticmethod
    def list_by_patient(patient_id: int, limit: int = 500) -> List[Alert]:
        return (Alert.query
                .filter_by(patient_id=patient_id)
                .order_by(Alert.ts.desc())
                .limit(limit)
                .all())
