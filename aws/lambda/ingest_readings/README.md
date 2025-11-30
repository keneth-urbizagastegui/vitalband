Objetivo
- Lambda `ingest_readings` recibe mensajes JSON desde AWS IoT Core y escribe en RDS MySQL en las tablas `devices`, `readings` y `device_telemetry`.

Formato del mensaje
- `{ "serial": "VB-0001", "heart_rate_bpm": 72, "spo2_pct": 98, "temp_c": 36.7, "motion_level": 2, "battery_mv": 4110, "battery_pct": 85, "rssi_dbm": -62 }`

Variables de entorno
- `DB_SECRET_ARN`: ARN del secreto en Secrets Manager con JSON `{"username","password","host","port","dbname"}`.

Permisos IAM mínimos
- `secretsmanager:GetSecretValue` para el secreto referenciado.
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` para CloudWatch.

Despliegue
- Crear función Lambda (Python 3.12) y subir `handler.py` como código.
- Adjuntar capa o incluir `pymysql` si se usa zip; alternativamente empaquetar con container.
- Configurar variable `DB_SECRET_ARN`.

Regla de AWS IoT Core
- Crear regla con `SELECT * FROM 'vitalband/readings'`.
- Acción: Invocar la función Lambda `ingest_readings`.
- Probar publicando desde el firmware.
