Despliegue en AWS
- Base de datos: RDS MySQL
- Ingesta: IoT Core → Lambda → RDS
- Backend: ECS Fargate (Docker + Gunicorn)
- Frontend: S3 + CloudFront
- Observabilidad: CloudWatch Logs

RDS MySQL
1. Crear instancia RDS (MySQL 8.x), security group y subredes privadas.
2. Ejecutar `backend/db/schema.sql`.
3. Crear secreto en Secrets Manager (JSON: host, port, username, password, dbname).

IoT Core
1. Crear política y certs para el dispositivo.
2. Tópico MQTT `vitalband/readings`.
3. Regla: `SELECT * FROM 'vitalband/readings'` → Acción Lambda.

Lambda
1. Código: `aws/lambda/ingest_readings/handler.py`.
2. Env: `DB_SECRET_ARN`.
3. Permisos: `secretsmanager:GetSecretValue` + logs.

Backend (ECS Fargate)
1. Construir imagen: `docker build -t vitalband-backend backend/`.
2. Publicar a ECR y crear Task Definition (puerto 8080).
3. Env vars: ver `backend/.env.example`.
4. Logs: driver `awslogs`.

Frontend (S3)
1. `cd frontend && npm ci && npm run build`.
2. Subir `dist/` a bucket S3, habilitar sitio estático y CloudFront.
