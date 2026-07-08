# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Plugin de prueba

- Plugins cargados desde `~/.config/opencode/opencode.json`

### Known Issues

- **Argon2 `memory_cost` desmedido**: `2**31` KiB (~2 TiB) en `PasswordService` causa latencia
  extrema o crash en cada operación de hash/verify. Corregir a `2**19` (512 MiB) o `2**20` (1 GiB).
- **Import incorrecto de `Session` en `dependencies.py`**: `app.models.session.Session` (ORM model)
  se usa como si fuera `sqlalchemy.orm.Session`. El `get_db_session` no puede funcionar.

## [0.1.0] - 2026-07-04 — Port a FastAPI

### Added

- FastAPI backend con `pyproject.toml` + `uv` (UV package manager)
- Uvicorn con hot reload para desarrollo
- Endpoints `/v1/users/` (list, create), `/v1/auth/*` (login, password reset)
- Sistema de autenticación con sessions via SQLAlchemy + PostgreSQL
- Flujo completo de password reset:
  - Solicitud (`POST /v1/auth/password/forgot`)
  - Verificación de token (`GET /v1/auth/password/verify`)
  - Reseteo (`POST /v1/auth/password/reset`)
- Envío de emails SMTP con `EmailService`
- Argon2id para hashing de contraseñas (`PasswordService`)
- S3/MinIO para file storage (`FileService` con signed URLs)
- Crypto utilities (SHA-256 hash, HMAC)
- Esquemas Pydantic de request/response
- Configuración vía `.env` con `pydantic-settings`
- Connection pool de base de datos (pool_size=10, max_overflow=20)

### Changed

- Portado de NestJS (TypeScript/Express) a FastAPI (Python)
- Migrado de MongoDB/Mongoose a PostgreSQL/SQLAlchemy 2.0
- Migrado de npm a uv para manejo de dependencias
- Switched de JWT a sessions con `pysessid` (token hex + SHA-256 hash en DB)
- Esquemas y DTOs migrados de class-validator a Pydantic v2

### Removed

- Todo el código fuente de NestJS (módulos, controladores, servicios, DTOs)
- MongoDB y Mongoose ODM
- Módulos de Message y Project (refactorizados, luego re-agregados en FastAPI)
- `requirements.txt` (reemplazado por `pyproject.toml` + `uv.lock`)

## [0.0.5] - 2026-05-15 — NestJS: Sesiones y estandarización

### Added

- `tsconfig.json` configuration
- Sesiones persistentes con Mongoose ODM
- Enums compartidos (tipo `ProjectStatus`, `PostStatus`)
- CORS con `allowedOrigins` definido por entorno
- Endpoint `/users/:id/sign-url` para file upload firmado S3
- Servicios de Roles y Export (vacíos, esqueleto)
- Estandarización de respuestas API (`ApiResponse`, `ApiError`)
- Atributos comunes extraídos en clases base de respuesta

### Changed

- Servicio de usuarios modificado, eliminado concepto 'team'
- DTOs unificados y tipados

### Fixed

- Correcciones menores en lógica de usuario y delivery

## [0.0.4] - 2026-04-07 — NestJS: CRUD resources

### Added

- Módulo completo de Projects con CRUD (5/5 subtareas)
- Módulo de Team Members con CRUD (3/5 subtareas)
- Módulo de Messages
- Endpoints `hq-update-member` y `hq-delete-member`
- Endpoint `GET /api/` (hello world)
- Endpoints adicionales de usuario + file upload

### Changed

- Mejoras en lógica de delivery de usuario

## [0.0.3] - 2026-03-02 — NestJS: Autenticación y password reset

### Added

- Módulo de autenticación v0.1
- Flujo de password reset:
  - Envío de email con token
  - Verificación de token
  - Reseteo de contraseña
- CRUD de proyectos (4/5)

## [0.0.2] - 2026-02-28 — NestJS: CRUD proyectos

### Added

- CRUD de proyectos v0.1 (4/5 subtareas)
- CRUD de team members v0.1

## [0.0.1] - 2026-02-28 — NestJS: Inicial

### Added

- Proyecto NestJS inicial con scaffold
- Autenticación de usuarios (login, registro)
- Flujo de usuarios completo
- Sesiones básicas
