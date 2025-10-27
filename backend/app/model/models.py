# backend/app/model/models.py
from datetime import datetime
from sqlalchemy import func, UniqueConstraint
from ..extensions import db


# -----------------------------
# Users (login y roles)
# -----------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    pass_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "client", name="user_role"), nullable=False, default="client")
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())

    # Relación 1:1 opcional con Patient (cuando role = client)
    patient = db.relationship("Patient", back_populates="user", uselist=False)


# -----------------------------
# Patients (perfil del cliente)
# -----------------------------
class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
                        unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    phone = db.Column(db.String(30))
    birthdate = db.Column(db.Date)
    sex = db.Column(db.Enum("male", "female", "other", "unknown", name="sex_enum"),
                    nullable=False, default="unknown")
    height_cm = db.Column(db.Numeric(5, 2))
    weight_kg = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())

    user = db.relationship("User", back_populates="patient")
    devices = db.relationship("Device", back_populates="patient", lazy=True)
    alerts = db.relationship("Alert", back_populates="patient", lazy=True)
    thresholds = db.relationship("Threshold", back_populates="patient", lazy=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


# -----------------------------
# Devices
# -----------------------------
class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="SET NULL", onupdate="CASCADE"))
    model = db.Column(db.String(80), nullable=False)
    serial = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.Enum("new", "active", "lost", "retired", "service", name="device_status"),
                       nullable=False, default="new")
    registered_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())

    patient = db.relationship("Patient", back_populates="devices")
    readings = db.relationship("Reading", back_populates="device", lazy=True, cascade="all, delete-orphan")
    telemetry = db.relationship("DeviceTelemetry", back_populates="device", lazy=True, cascade="all, delete-orphan")


# -----------------------------
# Readings (métricas biométricas)
# -----------------------------
class Reading(db.Model):
    __tablename__ = "readings"

    id = db.Column(db.BigInteger, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    ts = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp(), index=True)

    heart_rate_bpm = db.Column(db.SmallInteger)        # 20–250
    temp_c = db.Column(db.Numeric(4, 1))               # 30.0–45.0
    spo2_pct = db.Column(db.SmallInteger)              # 50–100
    motion_level = db.Column(db.SmallInteger)          # 0–10

    device = db.relationship("Device", back_populates="readings")


# -----------------------------
# Device Telemetry (batería/estado)
# -----------------------------
class DeviceTelemetry(db.Model):
    __tablename__ = "device_telemetry"

    id = db.Column(db.BigInteger, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id", ondelete="CASCADE", onupdate="CASCADE"),
                          nullable=False)
    ts = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp(), index=True)

    battery_mv = db.Column(db.SmallInteger)            # 3300–4300
    battery_pct = db.Column(db.SmallInteger)           # 0–100
    charging = db.Column(db.Boolean)                   # 0/1
    rssi_dbm = db.Column(db.SmallInteger)              # opcional
    board_temp_c = db.Column(db.Numeric(4, 1))         # opcional

    device = db.relationship("Device", back_populates="telemetry")


# -----------------------------
# Thresholds (umbrales)
# -----------------------------
class Threshold(db.Model):
    __tablename__ = "thresholds"
    __table_args__ = (UniqueConstraint("patient_id", "metric", name="ux_threshold_patient_metric"),)

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=True)  # NULL => global
    metric = db.Column(db.Enum("heart_rate", "temperature", "spo2", name="metric_enum"), nullable=False)
    min_value = db.Column(db.Numeric(6, 2))
    max_value = db.Column(db.Numeric(6, 2))
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())

    patient = db.relationship("Patient", back_populates="thresholds")


# -----------------------------
# Alerts
# -----------------------------
class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.BigInteger, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id", ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=False)
    ts = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    type = db.Column(db.Enum("tachycardia", "bradycardia", "fever", "hypoxia", "custom", name="alert_type"), nullable=False)
    severity = db.Column(db.Enum("low", "moderate", "high", "critical", name="alert_severity"),
                         nullable=False, default="low")
    message = db.Column(db.String(255))
    acknowledged_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    acknowledged_at = db.Column(db.DateTime)

    patient = db.relationship("Patient", back_populates="alerts")
    acknowledged_user = db.relationship("User", foreign_keys=[acknowledged_by])
