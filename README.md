# VitalBand: Plataforma de Monitoreo de Salud Full-Stack

[![CI de Backend](https://github.com/keneth-urbizagastegui/vitalband/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/keneth-urbizagastegui/vitalband/actions/workflows/backend-ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**VitalBand** es una aplicación web completa diseñada para el monitoreo remoto de pacientes. Utiliza un stack moderno con **Flask (Python)** para el backend y **React (TypeScript)** para el frontend.

La plataforma permite a los pacientes (Clientes) monitorear sus signos vitales enviados por un dispositivo, ver su historial y recibir alertas. Al mismo tiempo, proporciona un potente Panel de Administración para gestionar pacientes, dispositivos y configurar los umbrales de alerta del sistema.

## 📂 Estructura del Proyecto

El proyecto es un monorepo que contiene dos aplicaciones principales:

* **`/backend`**: Una API RESTful de Flask que sigue una arquitectura limpia (Controlador -> Servicio -> Repositorio) para manejar toda la lógica de negocio y la interacción con la base de datos.
* **`/frontend`**: una Aplicación de Página Única (SPA) moderna construida con Vite, React y TypeScript, que consume la API del backend.

---

## 🛠️ Stack Tecnológico

| Backend (Servidor) | Frontend (Cliente) |
| :--- | :--- |
| ✅ **Python 3.11+** | ✅ **React 19** (con Vite) |
| ✅ **Flask** (Framework de API) | ✅ **TypeScript** |
| ✅ **SQLAlchemy** (ORM) | ✅ **Tailwind CSS** (Estilos) |
| ✅ **MySQL** (Base de datos) | ✅ **React Router v7** (Rutas) |
| ✅ **Flask-JWT-Extended** (Autenticación) | ✅ **Axios** (Cliente HTTP) |
| ✅ **Marshmallow** (Validación / DTOs) | ✅ **Recharts** (Gráficos) |
| ✅ **Alembic** (Migraciones de BD) | ✅ **React Context** (Gestión de estado) |
| ✅ **Pytest** (Pruebas) | |

---

## ✨ Características Implementadas

### 🔑 Autenticación y Roles
* **Inicio de sesión con JWT** (`/login`).
* **Registro de nuevos pacientes** (`/signup`).
* **Recuperación de contraseña** (`/forgot`).
* **Rutas Protegidas** y **Guardias de Rol** para separar las vistas de `admin` y `client`.

### 👑 Portal de Administración
* **Dashboard de Admin** con estadísticas (total de pacientes, dispositivos) y un panel de "Alertas Pendientes".
* **CRUD de Pacientes:**
    * **Crear** nuevos pacientes (incluyendo la creación de su cuenta de usuario).
    * **Leer** la lista de todos los pacientes.
    * **Leer** los detalles de un paciente específico.
    * **Actualizar** la información personal de un paciente.
    * **Eliminar** un paciente (y su usuario asociado).
* **CRUD de Dispositivos:**
    * **Crear** (registrar) nuevos dispositivos de hardware.
    * **Leer** la lista de todos los dispositivos.
    * **Asignar/Desasignar** dispositivos a pacientes a través de un modal.
    * **Eliminar** un dispositivo.
* **Gestión de Alertas:**
    * Ver la lista de alertas por paciente.
    * **Reconocer (Acknowledge)** una alerta pendiente.
* **Configuración del Sistema:**
    * Establecer **umbrales globales** (ej. min/max de ritmo cardíaco) para todo el sistema.
    * Establecer **umbrales personalizados** por paciente que sobreescriben los globales.

### 👤 Portal del Cliente (Paciente)
* **Dashboard de Paciente** con tarjetas de métricas en tiempo real (HR, SpO2, Temp) y gráficos de las últimas 24 horas.
* **Historial de Métricas** con gráficos y un selector de rango de fechas.
* **Mis Alertas** para ver todas las alertas personales, marcando las que están "Pendientes" o "Vistas por Admin".
* **Mi Perfil** para revisar la información personal y del dispositivo asignado.

---

## 🚀 Cómo Empezar

Sigue estas instrucciones para levantar el proyecto completo en tu máquina local.

### Prerrequisitos
* **Python 3.11+**
* **Node.js 18+**
* Un servidor de base de datos **MySQL** (o MariaDB) funcionando.

### 1. Configuración de la Base de Datos

Primero, necesitas crear la base de datos y sus tablas.

1.  Abre tu cliente de MySQL (DBeaver, phpMyAdmin, o la terminal).
2.  Crea la base de datos:
    ```sql
    CREATE DATABASE IF NOT EXISTS vitalband
      CHARACTER SET utf8mb4
      COLLATE utf8mb4_unicode_ci;
    ```
3.  Carga el esquema de la base de datos (asegúrate de estar en la raíz del proyecto):
    ```bash
    mysql -u root -p vitalband < backend/db/schema.sql
    ```
4.  Inserta los datos de demostración (admin y paciente "Ana"):
    ```bash
    mysql -u root -p vitalband < backend/db/seed.sql
    ```

### 2. Ejecutar el Backend (Flask)

1.  Abre una terminal y navega a la carpeta del backend.
    ```bash
    cd backend
    ```
2.  Crea y activa un entorno virtual:
    ```bash
    # macOS / Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows (PowerShell)
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
3.  Instala las dependencias de Python:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crea tu archivo de variables de entorno `.env` en la carpeta `backend/`. (Puedes copiar `.env.example` si existe o crear uno nuevo).

    **Contenido para `backend/.env`:** (Ajusta los valores de tu BD)
    ```ini
    # --- Base de Datos ---
    DB_USER=root
    DB_PASS=tu_contraseña_de_mysql
    DB_HOST=127.0.0.1
    DB_NAME=vitalband

    # --- Seguridad ---
    FLASK_DEBUG=1
    SECRET_KEY=un-secreto-largo-y-dificil-para-flask
    JWT_SECRET_KEY=un-secreto-diferente-para-jwt
    ```
5.  ¡Ejecuta el servidor de backend!
    ```bash
    flask run
    ```
    El backend estará corriendo en `http://127.0.0.1:5000`.

### 3. Ejecutar el Frontend (React)

1.  Abre una **segunda terminal** y navega a la carpeta del frontend.
    ```bash
    cd frontend
    ```
2.  Instala las dependencias de Node.js:
    ```bash
    npm install
    ```
3.  Crea tu archivo de entorno local `.env.local` en la carpeta `frontend/`.

    **Contenido para `frontend/.env.local`:** (Apunta a tu backend)
    ```ini
    VITE_API_URL=[http://127.0.0.1:5000/api/v1](http://127.0.0.1:5000/api/v1)
    ```
4.  ¡Ejecuta el servidor de desarrollo!
    ```bash
    npm run dev
    ```
    El frontend estará corriendo en `http://localhost:5173`.

---

## 👤 Inicios de Sesión de Demostración

Puedes usar estos usuarios (creados por `backend/db/seed.sql`) para probar la aplicación:

* **Administrador:**
    * **Email:** `admin@vitalband.local`
    * **Contraseña:** `Admin123!`

* **Paciente (Cliente):**
    * **Email:** `ana@demo.com`
    * **Contraseña:** `Admin123!`

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.