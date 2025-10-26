from marshmallow import Schema, fields

class LoginRequest(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

class PatientCreateRequest(Schema):
    full_name = fields.String(required=True)
    email = fields.Email(required=False)
