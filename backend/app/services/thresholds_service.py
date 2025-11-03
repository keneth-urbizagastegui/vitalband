from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal
from ..model.models import Threshold
# si creaste el repo opcional:
try:
    from ..repository.thresholds_repository import ThresholdsRepository
except Exception:
    ThresholdsRepository = None  # por si aún no lo agregaste

class ThresholdsService:
    def __init__(self, repo: Optional["ThresholdsRepository"] = None):
        self.repo = repo or (ThresholdsRepository() if ThresholdsRepository else None)

    def get_thresholds(self, patient_id: Optional[int], metric: str) -> Threshold:
        """
        Obtiene un objeto Threshold desde el repositorio. Si no existe, devuelve un
        objeto Threshold temporal (no persistido) con valores por defecto.

        También realiza fallback a umbral global (patient_id=None) cuando se solicita
        uno específico de paciente y no existe.
        """
        # Si existe repositorio, intenta obtener primero el umbral específico
        if self.repo:
            t: Optional[Threshold] = self.repo.get(patient_id, metric)
            if t:
                return t

            # Fallback: intenta obtener el umbral global si no hay específico
            t_global: Optional[Threshold] = self.repo.get(None, metric)
            if t_global:
                return t_global

        # Si no hay repo o no se encontró nada, construye un Threshold temporal con defaults
        defaults = {
            "heart_rate": {"min": 50, "max": 120},
            "temperature": {"min": 35.5, "max": 38.0},
            "spo2": {"min": 92, "max": 100},
        }

        d = defaults.get(metric, {"min": None, "max": None})
        # Para defaults globales, marcamos patient_id=None para indicar que es global
        temp_patient_id = None if patient_id is not None else patient_id
        return Threshold(
            patient_id=temp_patient_id,
            metric=metric,
            min_value=(Decimal(str(d.get("min"))) if d.get("min") is not None else None),
            max_value=(Decimal(str(d.get("max"))) if d.get("max") is not None else None),
            created_at=datetime.now(timezone.utc)
        )

    def upsert_thresholds(self, patient_id: int | None, metric: str,
                          min_value=None, max_value=None) -> Optional[Threshold]:
        if not self.repo:
            raise RuntimeError("ThresholdsRepository no disponible.")
        return self.repo.upsert(patient_id, metric, min_value, max_value)
