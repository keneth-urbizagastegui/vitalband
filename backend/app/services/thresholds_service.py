from typing import Optional, Dict, Any
from ..model.models import Threshold
# si creaste el repo opcional:
try:
    from ..repository.thresholds_repository import ThresholdsRepository
except Exception:
    ThresholdsRepository = None  # por si aún no lo agregaste

class ThresholdsService:
    def __init__(self, repo: Optional["ThresholdsRepository"] = None):
        self.repo = repo or (ThresholdsRepository() if ThresholdsRepository else None)

    def get_thresholds(self, patient_id: int | None, metric: str) -> Dict[str, Any]:
        """
        Si hay repo, lee de BD; si no, devuelve defaults razonables.
        """
        if self.repo:
            t: Optional[Threshold] = self.repo.get(patient_id, metric)
            if t:
                return {"metric": metric, "min": float(t.min_value) if t.min_value is not None else None,
                        "max": float(t.max_value) if t.max_value is not None else None}
        # defaults (puedes ajustarlos)
        defaults = {
            "heart_rate": {"min": 50, "max": 120},
            "temperature": {"min": 35.5, "max": 38.0},
            "spo2": {"min": 92, "max": 100},
        }
        return {"metric": metric, **defaults.get(metric, {})}

    def upsert_thresholds(self, patient_id: int | None, metric: str,
                          min_value=None, max_value=None) -> Optional[Threshold]:
        if not self.repo:
            raise RuntimeError("ThresholdsRepository no disponible.")
        return self.repo.upsert(patient_id, metric, min_value, max_value)
