class ThresholdsService:
    def get_thresholds(self, patient_id: int | None, metric: str):
        # TODO: implementar lectura real de thresholds (global o por paciente)
        return {"metric": metric, "min": 50, "max": 120}
