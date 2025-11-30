# VitalBand

Proyecto de monitorización biométrica con hardware ESP32 y plataforma en la nube (AWS) que integra IoT Core, Lambda, RDS MySQL, backend Flask en ECS Fargate y frontend React en S3/CloudFront.

## Estructura
- `hardware/`: documentación y guía de firmware del dispositivo.
- `hardware/firmware/`: código fuente del firmware (ESP32, sensores).
- `hardware/tests/`: sketches de prueba por sensor.
- `backend/`: API Flask + SQLAlchemy + JWT + Alembic.
- `frontend/`: React + Vite + Tailwind.
- `aws/`: Lambda de ingesta y plan de arquitectura.
- `docs/`: notas de arquitectura y API.

## Arquitectura AWS
- `IoT Core`: recibe MQTT desde ESP32 (`vitalband/readings`).
- `Lambda (ingest_readings)`: procesa payload y escribe en `RDS MySQL`.
- `RDS MySQL`: esquema en `backend/db/schema.sql`.
- `ECS Fargate`: ejecuta backend con `Gunicorn` (`backend/Dockerfile`).
- `S3 + CloudFront`: entrega el frontend.
- `CloudWatch Logs`: registro de Lambda y backend.
- `Secrets Manager`: credenciales de BD.

## Inicio rápido
- Backend:
  - `cd backend && python -m venv .venv && .venv\\Scripts\\activate`
  - `pip install -r requirements.txt`
  - copiar `backend/.env.example` a `backend/.env` y ajustar.
  - `python run.py` → `GET http://127.0.0.1:5000/health`
- Frontend:
  - `cd frontend && npm ci && npm run dev`
  - abrir `http://localhost:5173`

## Seguridad
- `HARDWARE/credentials.h` está excluido por `.gitignore`.
- Usa `Secrets Manager` y `.env` locales; no publiques claves.

## Licencia
Ver `LICENSE`.
