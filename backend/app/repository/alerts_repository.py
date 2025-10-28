# backend/app/repository/alerts_repository.py

from typing import List, Optional
from datetime import datetime # Necesario para acknowledge
from ..extensions import db
from ..model.models import Alert

class AlertsRepository:
    @staticmethod
    def list_by_patient(patient_id: int, limit: int = 500) -> List[Alert]:
        """Obtiene una lista de alertas para un paciente, ordenadas por fecha descendente."""
        return (Alert.query
                .filter_by(patient_id=patient_id)
                .order_by(Alert.ts.desc())
                .limit(limit)
                .all())

    # --- NUEVO: Obtener Alerta por ID ---
    @staticmethod
    def get_by_id(alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta específica por su ID primario."""
        # Usa db.session.get para buscar por clave primaria
        return db.session.get(Alert, alert_id)
        # Alternativa: return Alert.query.get(alert_id)

    # --- NUEVO: Marcar Alerta como Reconocida ---
    @staticmethod
    def acknowledge(alert: Alert, user_id: int, timestamp: datetime, notes: Optional[str] = None) -> Alert:
        """
        Actualiza los campos 'acknowledged_by' y 'acknowledged_at' de una alerta.
        Opcionalmente, podría actualizar un campo 'notes' si existiera en el modelo.
        """
        alert.acknowledged_by = user_id
        alert.acknowledged_at = timestamp
        # Si tuvieras un campo para notas en el modelo Alert:
        # if notes is not None and hasattr(alert, 'acknowledgement_notes'):
        #     alert.acknowledgement_notes = notes

        # No es necesario db.session.add(alert) porque ya está en la sesión
        db.session.commit() # Guarda los cambios en la BD
        db.session.refresh(alert) # Refresca el objeto
        return alert

    # --- Opcional: Métodos para estadísticas (ej. contar por severidad) ---
    # @staticmethod
    # def count_recent_by_severity(hours: int = 24) -> Dict[str, int]:
    #     """Cuenta alertas de las últimas 'hours' horas, agrupadas por severidad."""
    #     from sqlalchemy import func, case
    #     from datetime import timedelta, timezone
    #
    #     since = datetime.now(timezone.utc) - timedelta(hours=hours)
    #
    #     # Define las severidades esperadas
    #     severities = ['low', 'moderate', 'high', 'critical']
    #
    #     # Construye la consulta de agregación
    #     counts = db.session.query(
    #         Alert.severity,
    #         func.count(Alert.id)
    #     ).filter(
    #         Alert.ts >= since
    #     ).group_by(
    #         Alert.severity
    #     ).all() # Ejecuta la consulta
    #
    #     # Convierte el resultado (lista de tuplas) en un diccionario,
    #     # asegurando que todas las severidades estén presentes con valor 0 si no hay alertas.
    #     result_dict = {severity: 0 for severity in severities}
    #     result_dict.update(dict(counts)) # Actualiza con los conteos reales
    #
    #     return result_dict