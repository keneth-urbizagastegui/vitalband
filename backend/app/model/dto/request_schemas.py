# backend/app/model/dto/request_schemas.py

import os
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load

# --- Helper de Validación para Password (ejemplo) ---
def validate_password(password):
    """Valida que la contraseña tenga al menos 8 caracteres, una mayúscula, una minúscula y un número."""
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isupper() for c in password):
        raise ValidationError("La contraseña debe contener al menos una mayúscula.")
    if not any(c.islower() for c in password):
        raise ValidationError("La contraseña debe contener al menos una minúscula.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("La contraseña debe contener al menos un número.")
    # Puedes añadir más reglas (ej. caracteres especiales)


# ---------- Auth ----------
class LoginRequest(Schema):
    """Schema para validar el payload de login."""
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True) # load_only evita que se serialice en respuestas

# --- NUEVO: Register Request ---
class RegisterRequest(Schema):
    """Schema para validar el payload de registro."""
    name = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate_password)
    # Opcional: Confirmación de contraseña (validación extra)
    confirm_password = fields.String(required=True, load_only=True)

    @validates("confirm_password")
    def validate_confirm_password(self, value, **kwargs):
        """Verifica que la confirmación coincida con la contraseña."""
        # Accede a los datos ya procesados (incluyendo 'password')
        if self.context.get('password') != value:
            raise ValidationError("Las contraseñas no coinciden.")

    # Sobrescribe load para pasar 'password' al contexto de validación de 'confirm_password'
    def load(self, data, *, many=None, partial=None, unknown=None):
        self.context['password'] = data.get('password')
        return super().load(data, many=many, partial=partial, unknown=unknown)


# --- NUEVO: Forgot Password Request ---
class ForgotPasswordRequest(Schema):
    """Schema para validar la solicitud de reseteo de contraseña."""
    email = fields.Email(required=True)

# --- NUEVO: Reset Password Request ---
class ResetPasswordRequest(Schema):
    """Schema para validar el payload de reseteo de contraseña."""
    token = fields.String(required=True) # El token recibido por email
    new_password = fields.String(required=True, load_only=True, validate=validate_password)
    # Opcional: Confirmación
    confirm_new_password = fields.String(required=True, load_only=True)

    @validates("confirm_new_password")
    def validate_confirm_new_password(self, value, **kwargs):
        if self.context.get('new_password') != value:
            raise ValidationError("Las nuevas contraseñas no coinciden.")

    def load(self, data, *, many=None, partial=None, unknown=None):
        self.context['new_password'] = data.get('new_password')
        return super().load(data, many=many, partial=partial, unknown=unknown)


# ---------- Patients ----------
class PatientCreateRequest(Schema):
    """Schema para crear un paciente (llamado por admin)."""
    # Si el flujo requiere crear User y Patient juntos, ajusta esto.
    # Por ahora, asume que user_id se provee si ya existe el User.
    user_id = fields.Integer(required=True) # Requerido según la FK en el modelo
    first_name = fields.String(required=True, validate=validate.Length(min=1, max=80))
    last_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=False, allow_none=True) # Email de contacto, no necesariamente login
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))
    birthdate = fields.Date(required=False, allow_none=True, format='%Y-%m-%d') # Especifica formato
    sex = fields.String(required=False, allow_none=True,
                       validate=validate.OneOf(["male", "female", "other", "unknown"]))
    height_cm = fields.Decimal(required=False, allow_none=True, as_string=True, validate=validate.Range(min=50, max=250)) # Rango ejemplo
    weight_kg = fields.Decimal(required=False, allow_none=True, as_string=True, validate=validate.Range(min=1, max=500)) # Rango ejemplo

class PatientUpdateRequest(Schema):
    """Schema para actualizar un paciente (todos los campos opcionales)."""
    # Similar a Create, pero nada es 'required=True'
    first_name = fields.String(required=False, validate=validate.Length(min=1, max=80))
    last_name = fields.String(required=False, validate=validate.Length(min=1, max=120))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))
    birthdate = fields.Date(required=False, allow_none=True, format='%Y-%m-%d')
    sex = fields.String(required=False, allow_none=True,
                       validate=validate.OneOf(["male", "female", "other", "unknown"]))
    height_cm = fields.Decimal(required=False, allow_none=True, as_string=True, validate=validate.Range(min=50, max=250))
    weight_kg = fields.Decimal(required=False, allow_none=True, as_string=True, validate=validate.Range(min=1, max=500))
    # No incluimos user_id aquí, ya que no debería cambiarse en una actualización.


# ---------- Readings (ingesta biométrica - si tuvieras un endpoint específico) ----------
# Este schema no se usa actualmente en los controllers revisados (los datos vienen de telemetría o directo del device?)
# Si el ESP32 envía lecturas directas a un endpoint POST /readings, necesitarías algo así:
class ReadingCreateRequest(Schema):
    """Schema para validar una lectura biométrica enviada por el dispositivo."""
    # ts es opcional, si no viene, el backend usa la hora actual
    ts = fields.DateTime(required=False, allow_none=True) # Formato ISO 8601
    heart_rate_bpm = fields.Integer(required=False, allow_none=True,
                                    validate=validate.Range(min=20, max=250))
    temp_c = fields.Decimal(required=False, allow_none=True, as_string=True,
                            validate=validate.Range(min=30.0, max=45.0)) # Rango temperatura corporal
    spo2_pct = fields.Integer(required=False, allow_none=True,
                              validate=validate.Range(min=50, max=100))
    motion_level = fields.Integer(required=False, allow_none=True,
                                  validate=validate.Range(min=0, max=10))


# ---------- Devices ----------
# --- NUEVO: Device Create Request (para admin) ---
class DeviceCreateRequest(Schema):
    """Schema para registrar un nuevo dispositivo."""
    serial = fields.String(required=True, validate=validate.Length(min=3, max=64))
    model = fields.String(required=True, validate=validate.Length(min=2, max=80))
    # Status y patient_id son opcionales al crear, con defaults en el servicio/repo
    status = fields.String(required=False, allow_none=True,
                          validate=validate.OneOf(["new", "active", "lost", "retired", "service"]))
    patient_id = fields.Integer(required=False, allow_none=True)

# --- NUEVO: Device Update Request (para admin) ---
class DeviceUpdateRequest(Schema):
    """Schema para actualizar un dispositivo (campos opcionales)."""
    # Solo permite actualizar model y status
    model = fields.String(required=False, validate=validate.Length(min=2, max=80))
    status = fields.String(required=False, allow_none=True,
                          validate=validate.OneOf(["new", "active", "lost", "retired", "service"]))
    # Serial y patient_id no se actualizan aquí (patient_id usa /assign)

# --- NUEVO: Device Assign Request (para admin) ---
class DeviceAssignRequest(Schema):
    """Schema para asignar/desasignar un dispositivo."""
    # Permite enviar null para desasignar
    patient_id = fields.Integer(required=True, allow_none=True)


# ---------- Telemetría de dispositivo (ya estaba) ----------
class DeviceTelemetryRequest(Schema):
    """Schema para validar datos de telemetría enviados por el dispositivo."""
    ts = fields.DateTime(required=False, allow_none=True) # Si no viene, backend usa hora actual
    battery_mv = fields.Integer(required=False, allow_none=True,
                                validate=validate.Range(min=2800, max=4500)) # Rango LiPo típico
    battery_pct = fields.Integer(required=False, allow_none=True,
                                 validate=validate.Range(min=0, max=100))
    charging = fields.Boolean(required=False, allow_none=True) # True/False
    rssi_dbm = fields.Integer(required=False, allow_none=True,
                              validate=validate.Range(min=-120, max=0)) # Rango típico dBm
    board_temp_c = fields.Decimal(required=False, allow_none=True, as_string=True,
                                  validate=validate.Range(min=-20.0, max=85.0)) # Rango temp. electrónica


# ---------- Thresholds ----------
# --- NUEVO: Threshold Update Request (para admin) ---
class ThresholdUpdateRequest(Schema):
    """Schema para establecer/actualizar un umbral."""
    # min_value y max_value son opcionales (puedes establecer solo uno)
    min_value = fields.Decimal(required=False, allow_none=True, as_string=True,
                               validate=validate.Range(min=0)) # Ajusta rangos según métrica si es necesario
    max_value = fields.Decimal(required=False, allow_none=True, as_string=True,
                               validate=validate.Range(min=0))

    # Validación adicional: min no puede ser mayor que max si ambos están presentes
    @validates("max_value")
    def validate_min_max(self, value, **kwargs):
        min_val = self.context.get('min_value')
        # Convierte a float/Decimal para comparar si ambos existen
        if min_val is not None and value is not None:
             try:
                  if float(min_val) > float(value):
                       raise ValidationError("El valor mínimo no puede ser mayor que el valor máximo.")
             except ValueError:
                  raise ValidationError("Valores min/max inválidos.")

    def load(self, data, *, many=None, partial=None, unknown=None):
        # Pasa min_value al contexto para la validación cruzada
        self.context['min_value'] = data.get('min_value')
        return super().load(data, many=many, partial=partial, unknown=unknown)


# ---------- Alerts ----------
# --- NUEVO: Alert Acknowledge Request (para admin) ---
class AlertAcknowledgeRequest(Schema):
    """Schema (opcional) para reconocer una alerta."""
    # Podrías añadir un campo para notas si quisieras
    notes = fields.String(required=False, allow_none=True, validate=validate.Length(max=255))


# ---------- Chatbot ----------
# Configurable: longitud máxima de entrada del chatbot (por entorno)
CHATBOT_MAX_INPUT_LEN = int(os.getenv('CHATBOT_MAX_INPUT_LEN', 1000))

# --- NUEVO: Chatbot Query Request ---
class ChatbotQueryRequest(Schema):
    """Schema para validar la consulta enviada al chatbot."""
    message = fields.String(
        required=True,
        validate=validate.Length(
            min=1,
            max=CHATBOT_MAX_INPUT_LEN,
            error=f"El mensaje no puede estar vacío o tener más de {CHATBOT_MAX_INPUT_LEN} caracteres."
        )
    ) # Limita longitud

    @pre_load
    def strip_message(self, data, **kwargs):
        """Elimina espacios en el campo 'message' antes de validar.
        Si después del strip queda vacío, la validación Length(min=1) lo rechazará.
        """
        if isinstance(data, dict):
            msg = data.get("message")
            if isinstance(msg, str):
                data["message"] = msg.strip()
        return data