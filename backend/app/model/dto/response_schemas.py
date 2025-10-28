# backend/app/model/dto/response_schemas.py

from marshmallow import Schema, fields

# --- NUEVO: User Response ---
class UserResponse(Schema):
    """Schema para la información pública del usuario."""
    id = fields.Integer(required=True)
    name = fields.String(required=True) # Nombre del usuario
    email = fields.Email(required=True)
    role = fields.String(required=True) # 'admin' o 'client'
    # No incluimos pass_hash por seguridad

# ---------- Patients ----------
class PatientResponse(Schema):
    """Schema detallado para un paciente."""
    id = fields.Integer(required=True)
    user_id = fields.Integer(required=True) # ID del User asociado
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    # Método para obtener el nombre completo, conveniente para el frontend
    full_name = fields.Method("get_full_name", dump_only=True)
    email = fields.Email(allow_none=True) # Email de contacto del paciente (puede diferir del login)
    phone = fields.String(allow_none=True)
    birthdate = fields.Date(allow_none=True)
    sex = fields.String(required=True)
    height_cm = fields.Decimal(as_string=True, allow_none=True)
    weight_kg = fields.Decimal(as_string=True, allow_none=True)
    created_at = fields.DateTime(required=True)

    def get_full_name(self, obj) -> str:
        """Combina nombre y apellido."""
        # Asegura que obj tenga los atributos (viene del modelo Patient)
        first = getattr(obj, "first_name", "") or ""
        last = getattr(obj, "last_name", "") or ""
        return f"{first} {last}".strip()

# --- NUEVO: Device Response ---
class DeviceResponse(Schema):
    """Schema para la información de un dispositivo."""
    id = fields.Integer(required=True)
    patient_id = fields.Integer(allow_none=True) # A qué paciente está asignado
    model = fields.String(required=True)
    serial = fields.String(required=True)
    status = fields.String(required=True) # 'new', 'active', etc.
    registered_at = fields.DateTime(required=True)
    # Podrías añadir campos relacionados si fueran necesarios, ej:
    # patient = fields.Nested(PatientResponse, only=("id", "full_name"), allow_none=True)

# ---------- Readings ----------
class ReadingResponse(Schema):
    """Schema para una lectura biométrica."""
    id = fields.Integer(required=True)
    device_id = fields.Integer(required=True)
    ts = fields.DateTime(required=True) # Timestamp de la lectura
    heart_rate_bpm = fields.Integer(allow_none=True)
    temp_c = fields.Decimal(as_string=True, allow_none=True, places=1) # Formato con 1 decimal
    spo2_pct = fields.Integer(allow_none=True)
    motion_level = fields.Integer(allow_none=True)

# ---------- Telemetría de dispositivo ----------
class DeviceTelemetryResponse(Schema):
    """Schema para un registro de telemetría del dispositivo."""
    id = fields.Integer(required=True)
    device_id = fields.Integer(required=True)
    ts = fields.DateTime(required=True) # Timestamp del registro
    battery_mv = fields.Integer(allow_none=True)
    battery_pct = fields.Integer(allow_none=True)
    charging = fields.Boolean(allow_none=True)
    rssi_dbm = fields.Integer(allow_none=True)
    board_temp_c = fields.Decimal(as_string=True, allow_none=True, places=1) # Formato con 1 decimal

# --- NUEVO: Threshold Response ---
class ThresholdResponse(Schema):
    """Schema para un umbral (límite para alertas)."""
    id = fields.Integer(required=True)
    patient_id = fields.Integer(allow_none=True) # Null si es global
    metric = fields.String(required=True) # 'heart_rate', 'temperature', 'spo2'
    min_value = fields.Decimal(as_string=True, allow_none=True)
    max_value = fields.Decimal(as_string=True, allow_none=True)
    created_at = fields.DateTime(required=True)

# --- NUEVO: Alert Response ---
class AlertResponse(Schema):
    """Schema para una alerta generada."""
    id = fields.Integer(required=True)
    patient_id = fields.Integer(required=True)
    ts = fields.DateTime(required=True) # Timestamp de la alerta
    type = fields.String(required=True) # 'tachycardia', 'fever', etc.
    severity = fields.String(required=True) # 'low', 'moderate', etc.
    message = fields.String(allow_none=True)
    acknowledged_by = fields.Integer(allow_none=True) # ID del User que reconoció
    acknowledged_at = fields.DateTime(allow_none=True) # Timestamp del reconocimiento
    # Opcional: Incluir info básica del paciente o del usuario que reconoció
    # patient = fields.Nested(PatientResponse, only=("id", "full_name"), allow_none=True)
    # acknowledged_user = fields.Nested(UserResponse, only=("id", "name"), allow_none=True)

# --- NUEVO: Chatbot Response ---
class ChatbotResponse(Schema):
    """Schema simple para la respuesta del chatbot."""
    reply = fields.String(required=True) # El texto de la respuesta