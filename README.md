# HQ Backend

FastAPI backend for the HQ Website.

---

## Instalación

### 1. Instalar uv

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Recargá la terminal y verificá:

```powershell
uv --version
```

### 2. Clonar y entrar al proyecto

```powershell
git clone <repo-url>
cd hq-backend
```

### 3. Sincronizar dependencias

```powershell
uv sync --all-groups
```

Esto crea `.venv/` automáticamente e instala todas las dependencias (producción + desarrollo).

### 4. Configurar variables de entorno

Copiá y completá el archivo de entorno:

```powershell
copy .env.example .env
```

Editá `.env` con los valores reales (DB, SMTP, etc.).

---

## Cómo correr la app

```powershell
uv run python -m app.main
```

Esto arranca Uvicorn con hot reload en `http://127.0.0.1:8000`.

### Alternativa directa

```powershell
uv run uvicorn app.main:app --reload
```

---

## Dependencias

### Producción

| Paquete | Rol en el proyecto |
|---------|-------------------|
| **fastapi** | Web framework. Define routers, valida requests/responses, genera OpenAPI docs. |
| **sqlalchemy** | ORM y SQL toolkit. Mapea las tablas de la DB a objetos Python (modelos en `app/models/`). |
| **psycopg[binary]** | Driver de PostgreSQL. SQLAlchemy lo usa para conectarse a Postgres. La variante `[binary]` incluye libpq empaquetado (necesario en Windows). |
| **pydantic** | Validación de datos. Define schemas de request/response con tipos y reglas. |
| **pydantic-settings** | Carga configuración desde `.env` en la clase `Settings` (`app/config/settings.py`). |
| **argon2-cffi** | Hashing de contraseñas con Argon2id (estándar OWASP). |
| **boto3** | Cliente S3 / AWS para subir y leer archivos de object storage (S3, MinIO, etc.). |
| **cryptography** | Criptografía simétrica (AES-GCM) para cifrar tokens y datos sensibles. |
| **alembic** | Migraciones de base de datos para SQLAlchemy. |
| **jinja2** | Motor de plantillas para generar HTML de emails. |
| **apscheduler** | Programación de jobs en background (cleanup de sesiones, etc.). |

### Desarrollo

| Paquete | Rol |
|---------|------|
| **ruff** | Linter y formateador unificado (reemplaza flake8 + black + isort). |
| **basedpyright** | Type checker estático con mejor integración con Pydantic/FastAPI que mypy. |
| **pytest** | Test runner. |
| **pytest-cov** | Reporte de cobertura de tests. |
| **annotated-doc** | Documentación inline de parámetros con `Annotated[..., Doc("...")]`. |

---

## Comandos útiles

```powershell
uv sync               # Instalar/actualizar dependencias
uv sync --all-groups  # Incluir dev dependencies
uv add <paquete>      # Agregar nueva dependencia de producción
uv add --dev <paquete> # Agregar nueva dependencia de desarrollo
uv remove <paquete>   # Eliminar dependencia
uv lock               # Actualizar uv.lock sin instalar
uv run python -m app.main  # Correr la app
uv run pytest         # Correr tests
uv run ruff check     # Linter
uv run ruff format    # Formatear código
uv run basedpyright   # Type checking
```

---
