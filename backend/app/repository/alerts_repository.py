from ..model.models import Alert

class AlertsRepository:
    def list_by_patient(self, patient_id: int) -> list[Alert]:
        return Alert.query.filter_by(patient_id=patient_id).order_by(Alert.created_at.desc()).all()
