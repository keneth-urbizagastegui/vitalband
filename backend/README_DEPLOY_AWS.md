Backend en ECS Fargate
- Imagen Docker basada en `backend/Dockerfile` usando Gunicorn.
- Variables de entorno: ver `.env.example` y configurar mediante ECS Task Definition o Secrets Manager.
- Logging: usar `awslogs` driver apuntando a un grupo de CloudWatch Logs.

Puertos
- Contenedor escucha en `8080`.

Healthcheck
- Endpoint `GET /health` devuelve `{status:"ok"}`.

Build y push (ejemplo)
1. `docker build -t vitalband-backend:latest backend/`
2. `docker tag vitalband-backend:latest <AWS_ACCOUNT>.dkr.ecr.<region>.amazonaws.com/vitalband-backend:latest`
3. `docker push <AWS_ACCOUNT>.dkr.ecr.<region>.amazonaws.com/vitalband-backend:latest`
