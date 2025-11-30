Arquitectura AWS (plan)
- IoT Core: recibe MQTT desde ESP32 (`vitalband/readings`).
- Lambda `ingest_readings`: procesa payload y escribe en RDS MySQL.
- RDS MySQL: base de datos (ver `backend/db/schema.sql`).
- ECS Fargate: ejecuta backend Flask en Docker (ver `backend/Dockerfile`).
- S3 + CloudFront: aloja frontend Vite/React.
- CloudWatch Logs: logs de Lambda y del backend (via `awslogs`).
- Secrets Manager: almacena credenciales de la BD (`DB_SECRET_ARN`).

Pasos de integración
1) RDS MySQL
   - Crear instancia RDS MySQL y security group.
   - Crear usuario y base `vitalband`.
   - Aplicar `backend/db/schema.sql` y opcionalmente `seed.sql`.
   - Crear secreto en Secrets Manager (JSON con host, port, username, password, dbname).

2) IoT Core
   - Cargar certificados al firmware (`hardware/firmware/credentials.h`).
   - Política IoT para permitir `iot:Connect`/`iot:Publish` al tópico `vitalband/readings`.
   - Crear Regla: `SELECT * FROM 'vitalband/readings'` → Acción: Lambda `ingest_readings`.

3) Lambda
   - Código en `aws/lambda/ingest_readings/handler.py`.
   - Variable de entorno `DB_SECRET_ARN` con ARN del secreto.
   - Permisos IAM: `secretsmanager:GetSecretValue` y CloudWatch Logs.

4) Backend (ECS Fargate)
   - Construir y publicar imagen a ECR.
   - Task Definition con env vars (JWT, CORS) y conexión a RDS.
   - Logging `awslogs` a CloudWatch.

5) Frontend (S3)
   - `npm run build` en `frontend/`.
   - Subir `frontend/dist` a S3 y configurar CloudFront.

Ver `docs/architecture/deploy.md` para comandos y detalles.
