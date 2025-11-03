# backend/app/repository/alerts_repository.py

from typing import List, Optional, Dict
from datetime import datetime # Necesario para acknowledge
from ..extensions import db
from ..model.models import Alert
from sqlalchemy import func, case # Necesario para el conteo

class AlertsRepository:
    @staticmethod
    def list_by_patient(patient_id: int, limit: int = 500) -> List[Alert]:
        """Obtiene una lista de alertas para un paciente, ordenadas por fecha descendente."""
        return (Alert.query
                .filter_by(patient_id=patient_id)
                .order_by(Alert.ts.desc())
                .limit(limit)
                .all())

    # --- CÓDIGO FUNCIONAL AÑADIDO ---
    @staticmethod
    def get_by_id(alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta específica por su ID primario."""
        return db.session.get(Alert, alert_id)

    # --- CÓDIGO FUNCIONAL AÑADIDO ---
    @staticmethod
    def acknowledge(alert: Alert, user_id: int, timestamp: datetime, notes: Optional[str] = None) -> Alert:
        """
        Actualiza los campos 'acknowledged_by' y 'acknowledged_at' de una alerta.
        """
        alert.acknowledged_by = user_id
        alert.acknowledged_at = timestamp
        # NOTA: 'notes' no se guarda porque el modelo 'Alert' no tiene un campo para ello.
        
        db.session.commit() # Guarda los cambios en la BD
        db.session.refresh(alert) # Refresca el objeto
        return alert

    # --- CÓDIGO FUNCIONAL AÑADIDO (Para el paso 2) ---
    @staticmethod
    def list_pending(limit: int = 50) -> List[Alert]:
        """Obtiene las alertas pendientes (no reconocidas) más recientes de TODOS los pacientes."""
        return (Alert.query
                .filter(Alert.acknowledged_at.is_(None)) # Filtra donde acknowledged_at ES NULL
                .order_by(Alert.ts.desc()) # Las más nuevas primero
                .limit(limit)
                .all())

    # --- NUEVO: Listar alertas pendientes por paciente ---
    @staticmethod
    def list_pending_for_patient(patient_id: int, limit: int = 5) -> List[Alert]:
        """Obtiene las alertas pendientes (no reconocidas) para un paciente específico."""
        return (
            Alert.query
            .filter(
                Alert.patient_id == patient_id,
                Alert.acknowledged_at.is_(None)
            )
            .order_by(Alert.ts.desc())
            .limit(limit)
            .all()
        )

    # --- Opcional: Métodos para estadísticas (ej. contar por severidad) ---
    @staticmethod
    def count_recent_by_severity(hours: int = 24) -> Dict[str, int]:
        """Cuenta alertas de las últimas 'hours' horas, agrupadas por severidad."""
        
        from datetime import timedelta, timezone
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        # Define las severidades esperadas
        severities = ['low', 'moderate', 'high', 'critical']

        counts = db.session.query(
            Alert.severity,
            func.count(Alert.id)
        ).filter(
            Alert.ts >= since
        ).group_by(
            Alert.severity
        ).all() # Ejecuta la consulta
        
        result_dict = {severity: 0 for severity in severities}
        result_dict.update(dict(counts)) # Actualiza con los conteos reales
        
        return result_dict