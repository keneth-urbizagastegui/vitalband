# VitalBand – Monolito Flask (capas) + Frontend

Estructura base del proyecto con *stubs* para cada carpeta clave. Incluye:
- Flask + SQLAlchemy + Alembic (Flask-Migrate), CORS, JWT.
- Separación **controller / services / repository / model (DTOs)**.
- Carpeta `docs/` con esqueletos de arquitectura y OpenAPI.
- Scripts SQL base (`db/schema.sql`, `db/seed.sql`).

## Requisitos
- Python 3.11+
- MySQL/MariaDB funcionando
- Node 18+ (para el frontend)

## Arranque rápido (backend)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# Configura variables
cp .env.example .env  # y edita los valores

# Inicializa BD (si usas Alembic)
flask db init || true  # sólo si no existe la carpeta migrations
flask db migrate -m "bootstrap"
flask db upgrade

# Ejecuta
flask run  # o python run.py
```

## Frontend
En `frontend/` hay estructura mínima (archivos placeholder). Para crear un proyecto real con Vite:
```bash
# desde la raíz del repo:
npm create vite@latest frontend -- --template react-ts
cd frontend
npm i axios
# copia luego los archivos de src/api/http.ts y src/api/endpoints.ts de este esqueleto
npm run dev
```

## Variables de entorno clave
- `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`
- `SQLALCHEMY_DATABASE_URI` (opcional; si no se define, se arma con las anteriores)
- `JWT_SECRET_KEY`
- `CORS_ORIGINS` (coma-separado)

## Licencia
MIT


---
## Subir a GitHub (rápido)
```bash
git init
git add .
git commit -m "chore: bootstrap vitalband skeleton"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/vitalband.git
git push -u origin main
```
**Recomendado:** habilita "Actions" para correr el workflow `Backend CI`.
