from marshmallow import Schema, fields

class PatientResponse(Schema):
    id = fields.Integer()
    full_name = fields.String()
    email = fields.Email(allow_none=True)

class MetricResponse(Schema):
    id = fields.Integer()
    device_id = fields.Integer()
    ts = fields.DateTime()
    heart_rate = fields.Integer(allow_none=True)
    spo2 = fields.Integer(allow_none=True)
