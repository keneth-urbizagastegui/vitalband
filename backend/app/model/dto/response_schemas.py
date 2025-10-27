from marshmallow import Schema, fields

# ---------- Patients ----------
class PatientResponse(Schema):
    id         = fields.Integer()
    user_id    = fields.Integer()
    first_name = fields.String()
    last_name  = fields.String()
    # por comodidad en el frontend
    full_name  = fields.Method("get_full_name")
    email      = fields.Email(allow_none=True)
    phone      = fields.String(allow_none=True)
    birthdate  = fields.Date(allow_none=True)
    sex        = fields.String()
    height_cm  = fields.Decimal(as_string=True, allow_none=True)
    weight_kg  = fields.Decimal(as_string=True, allow_none=True)
    created_at = fields.DateTime()

    def get_full_name(self, obj):
        # si definiste property full_name en el modelo, puedes usar return obj.full_name
        first = getattr(obj, "first_name", "") or ""
        last  = getattr(obj, "last_name", "") or ""
        return (first + " " + last).strip()


# ---------- Readings ----------
class ReadingResponse(Schema):
    id             = fields.Integer()
    device_id      = fields.Integer()
    ts             = fields.DateTime()
    heart_rate_bpm = fields.Integer(allow_none=True)
    temp_c         = fields.Decimal(as_string=True, allow_none=True)
    spo2_pct       = fields.Integer(allow_none=True)
    motion_level   = fields.Integer(allow_none=True)


# ---------- Telemetría de dispositivo ----------
class DeviceTelemetryResponse(Schema):
    id           = fields.Integer()
    device_id    = fields.Integer()
    ts           = fields.DateTime()
    battery_mv   = fields.Integer(allow_none=True)
    battery_pct  = fields.Integer(allow_none=True)
    charging     = fields.Boolean(allow_none=True)
    rssi_dbm     = fields.Integer(allow_none=True)
    board_temp_c = fields.Decimal(as_string=True, allow_none=True)
