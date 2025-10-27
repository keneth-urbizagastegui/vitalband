from marshmallow import Schema, fields, validate

# ---------- Auth ----------
class LoginRequest(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


# ---------- Patients ----------
class PatientCreateRequest(Schema):
    # 1:1 con users cuando role=client (el user se crea aparte;
    # si en tu flujo ya tienes user_id, puedes incluirlo aquí como opcional)
    user_id   = fields.Integer(required=False)
    first_name = fields.String(required=True, validate=validate.Length(min=2, max=80))
    last_name  = fields.String(required=True, validate=validate.Length(min=2, max=120))
    email      = fields.Email(required=False, allow_none=True)
    phone      = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))
    birthdate  = fields.Date(required=False, allow_none=True)
    sex        = fields.String(required=False, allow_none=True,
                               validate=validate.OneOf(["male","female","other","unknown"]))
    height_cm  = fields.Decimal(required=False, allow_none=True, as_string=True)
    weight_kg  = fields.Decimal(required=False, allow_none=True, as_string=True)

class PatientUpdateRequest(Schema):
    # todo opcional
    first_name = fields.String(required=False, validate=validate.Length(min=2, max=80))
    last_name  = fields.String(required=False, validate=validate.Length(min=2, max=120))
    email      = fields.Email(required=False, allow_none=True)
    phone      = fields.String(required=False, allow_none=True, validate=validate.Length(max=30))
    birthdate  = fields.Date(required=False, allow_none=True)
    sex        = fields.String(required=False, allow_none=True,
                               validate=validate.OneOf(["male","female","other","unknown"]))
    height_cm  = fields.Decimal(required=False, allow_none=True, as_string=True)
    weight_kg  = fields.Decimal(required=False, allow_none=True, as_string=True)


# ---------- Readings (ingesta biométrica) ----------
class ReadingCreateRequest(Schema):
    ts             = fields.DateTime(required=False)  # si falta, server usa NOW()
    heart_rate_bpm = fields.Integer(required=False, allow_none=True,
                                    validate=validate.Range(min=20, max=250))
    temp_c         = fields.Decimal(required=False, allow_none=True, as_string=True)  # 30.0–45.0
    spo2_pct       = fields.Integer(required=False, allow_none=True,
                                    validate=validate.Range(min=50, max=100))
    motion_level   = fields.Integer(required=False, allow_none=True,
                                    validate=validate.Range(min=0, max=10))


# ---------- Telemetría de dispositivo ----------
class DeviceTelemetryRequest(Schema):
    ts          = fields.DateTime(required=False)
    battery_mv  = fields.Integer(required=False, allow_none=True,
                                 validate=validate.Range(min=3200, max=4400))
    battery_pct = fields.Integer(required=False, allow_none=True,
                                 validate=validate.Range(min=0, max=100))
    charging    = fields.Boolean(required=False, allow_none=True)
    rssi_dbm    = fields.Integer(required=False, allow_none=True)      # p.ej. -90..-20
    board_temp_c = fields.Decimal(required=False, allow_none=True, as_string=True)
