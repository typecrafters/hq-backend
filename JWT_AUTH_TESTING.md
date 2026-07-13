# JWT Auth — Guia de Testing Completa

## Setup

```bash
# 1. Crear .env con JWT_SECRET (minimo 32 caracteres)
echo "JWT_SECRET=una-clave-segura-de-al-menos-32-caracteres" >> .env

# 2. Arrancar el server
uv run uvicorn app.main:app --reload
```

**Base URL:** `http://localhost:8000/api/v1`

---

## 1. Login

### Caso exitoso

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "secret123", "rememberMe": false}'
```

**200** — respuesta:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```
**Cookie:** `pysessid=<hex>` (httponly, secure, samesite=lax)

### Credenciales incorrectas

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "wrong", "rememberMe": false}'
```

**401** — `{"detail": "Unauthorized."}`

### Remember me (cookie dura 90 dias)

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "secret123", "rememberMe": true}'
```

**200** — misma respuesta, pero la cookie `pysessid` tiene `Max-Age=7776000` (90 dias).

---

## 2. Refresh Token

El browser manda la cookie `pysessid` automaticamente. En curl hay que pasarla explicitamente.

### Caso exitoso

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/refresh \
  -b "pysessid=abc123..."
```

**200** — respuesta:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```

### Sin cookie

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh
```

**401** — `{"detail": "Unauthorized."}`

### Cookie invalida / session revocada

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh \
  -b "pysessid=invalidhash"
```

**401** — `{"detail": "Unauthorized."}`

### Cookie expirada

La session expira segun `DEFAULT_AGE` (7 dias) o `EXTENDED_AGE` (90 dias si `rememberMe`). Para testear, crea un usuario, espera a que expire la session, o modifica `expires_at` en la DB.

---

## 3. Logout

### Caso exitoso

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/logout \
  -b "pysessid=abc123..."
```

**204** — session revocada, cookie `pysessid` eliminada (`Set-Cookie: pysessid=; Max-Age=0`).

### Sin cookie

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/logout
```

**204** — no-op, no revoca nada pero devuelve 204 igual.

### Despues de logout, refresh falla

```bash
# Primero logout
curl -s -X POST http://localhost:8000/api/v1/auth/logout -b "pysessid=abc123..."

# Luego intentar refresh con la misma cookie
curl -s -X POST http://localhost:8000/api/v1/auth/refresh -b "pysessid=abc123..."
```

**401** — session ya revocada.

---

## 4. Ruta Protegida con Bearer Token

### GET /auth/me — obtener usuario actual

```bash
curl -v "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — respuesta:
```json
{
  "message": "User found",
  "item": {
    "id": 1,
    "email": "admin@example.com",
    "firstName": "Admin",
    "lastName": "User",
    "role": "admin",
    "permissions": ["read:message", "write:message"]
  }
}
```

### Sin token

```bash
curl -s "http://localhost:8000/api/v1/auth/me"
```

**401** — `{"detail": "Unauthorized."}`

### Token invalido

```bash
curl -s "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer invalid.token.here"
```

**401** — `{"detail": "Unauthorized."}`

### Token expirado

El token expira en `jwt_expiry_minutes` (default 15 min). Para testear:
1. Login y obtener token
2. Esperar 15+ minutos (o reducir `jwt_expiry_minutes` en .env)
3. Intentar usar el token

**401** — `{"detail": "Unauthorized."}`

---

## 5. Usuarios Protegidos

### GET /users/ — listar usuarios

```bash
curl -v "http://localhost:8000/api/v1/users/?page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — lista de usuarios

### Sin token

```bash
curl -s "http://localhost:8000/api/v1/users/?page=1&limit=10"
```

**401** — `{"detail": "Unauthorized."}`

### POST /users/ — crear usuario

```bash
curl -v -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"firstName": "New", "lastName": "User", "email": "new@example.com", "password": "pass123"}'
```

**201** — usuario creado

---

## 6. Mensajes — Permisos por rol

### GET /messages/ — listar mensajes (requiere `read:message`)

```bash
curl -v "http://localhost:8000/api/v1/messages/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — lista de mensajes

### Sin token

```bash
curl -s "http://localhost:8000/api/v1/messages/"
```

**401** — `{"detail": "Unauthorized."}`

### Sin permiso `read:message` (rol sin permisos)

```bash
# Login con un usuario que NO tiene read:message
curl -s "http://localhost:8000/api/v1/messages/" \
  -H "Authorization: Bearer <token-de-usuario-sin-permiso>"
```

**403** — `{"detail": "Forbidden."}`

### GET /messages/{id} — obtener mensaje por ID

```bash
curl -v "http://localhost:8000/api/v1/messages/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — mensaje encontrado
**404** — `{"detail": "Message not found"}`

### POST /messages/ — crear mensaje (PUBLICO, sin auth)

```bash
curl -v -X POST "http://localhost:8000/api/v1/messages/" \
  -H "Content-Type: application/json" \
  -d '{"fullName": "John Doe", "email": "john@example.com", "message": "Hello!"}'
```

**201** — mensaje creado. Este endpoint NO requiere autenticacion.

### PATCH /messages/{id}/read — marcar como leido (requiere `read:message`)

```bash
curl -v -X PATCH "http://localhost:8000/api/v1/messages/1/read" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — mensaje marcado como leido
**403** — sin permiso `read:message`
**404** — `{"detail": "Message not found"}`

### PATCH /messages/{id}/reply — responder mensaje (requiere `write:message`)

```bash
curl -v -X PATCH "http://localhost:8000/api/v1/messages/1/reply" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"reply": "Gracias por contactarnos!"}'
```

**200** — respuesta enviada
**403** — sin permiso `write:message`
**404** — `{"detail": "Message not found"}`

### DELETE /messages/{id} — eliminar mensaje (requiere `delete:message`)

```bash
curl -v -X DELETE "http://localhost:8000/api/v1/messages/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**204** — mensaje eliminado
**403** — sin permiso `delete:message`
**404** — `{"detail": "Message not found"}`

---

## 7. Password Reset

### Paso 1: Solicitar reset (forgot)

```bash
curl -v -X POST http://localhost:8000/api/v1/auth/password/forgot \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com"}'
```

**202** — accepted. Si el email existe, se envia un link. Si no existe, duerme 1 segundo (proteccion contra timing attacks) y devuelve 202 igual.

### Paso 2: Verificar token

```bash
curl -v "http://localhost:8000/api/v1/auth/password/verify?token=abc123..."
```

**204** — token valido
**401** — `{"detail": "Unauthorized."}` (token invalido, expirado, o ya consumido)

### Paso 3: Resetear password

```bash
curl -v -X POST "http://localhost:8000/api/v1/auth/password/reset?token=abc123..." \
  -H "Content-Type: application/json" \
  -d '{"password": "newpass123", "confirmPassword": "newpass123"}'
```

**200** — password actualizado
**401** — `{"detail": "Unauthorized."}` (token invalido/expirado)
**422** — `{"detail": "Passwords do not match."}` (si no coinciden)

### Token ya consumido

```bash
# Primer uso
curl -s -X POST "http://localhost:8000/api/v1/auth/password/reset?token=abc123..." \
  -H "Content-Type: application/json" \
  -d '{"password": "newpass123", "confirmPassword": "newpass123"}'

# Segundo intento con el mismo token
curl -s -X POST "http://localhost:8000/api/v1/auth/password/reset?token=abc123..." \
  -H "Content-Type: application/json" \
  -d '{"password": "anotherpass", "confirmPassword": "anotherpass"}'
```

**401** — token ya consumido

---

## 8. Sessions (gestion de sesiones)

### GET /auth/sessions — listar propias

```bash
curl -v "http://localhost:8000/api/v1/auth/sessions" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** — respuesta:
```json
{
  "message": "Session list found",
  "items": [
    {
      "hash": "abc123...",
      "ipAddress": "127.0.0.1",
      "userAgent": "curl/8.0",
      "issuedAt": "2026-07-12T10:00:00Z",
      "expiresAt": "2026-07-19T10:00:00Z"
    }
  ],
  "meta": { "count": 1 }
}
```

### DELETE /auth/sessions/{hash} — revocar sesion especifica

```bash
curl -v -X DELETE "http://localhost:8000/api/v1/auth/sessions/abc123..." \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**204** — sesion revocada
**403** — la sesion no pertenece al usuario actual

---

## 9. Tests Automatizados

```bash
# Todo el suite
uv run pytest -v

# Solo tests de auth
uv run pytest tests/unit/test_jwt_service.py tests/unit/test_auth_service_jwt.py -v

# Tests de integracion auth
uv run pytest tests/integration/test_auth_jwt.py -v

# Tests de usuarios protegidos
uv run pytest tests/integration/test_users_auth.py -v

# Todos los tests de auth (unit + integration)
uv run pytest -k "jwt or auth or password" -v

# Coverage
uv run pytest --cov=app --cov-report=term-missing
```

---

## Flujo Completo (SPA / Mobile)

```
1. POST /api/v1/auth/login           → login, recibis accessToken + cookie pysessid
2. GET  /api/v1/users con Bearer     → usás accessToken del paso 1
3. GET  /api/v1/auth/me con Bearer  → verificás tu identidad
4. GET  /api/v1/auth/sessions        → listás tus sesiones activas
5. Cuando el token expira (15 min):
   POST /api/v1/auth/refresh         → browser manda cookie, recibís nuevo accessToken
6. POST /api/v1/auth/logout          → browser manda cookie, se revoca la sesión
7. POST /api/v1/auth/password/forgot → solicitás reset, recibís email
8. GET  /api/v1/auth/password/verify → verificás el token del email
9. POST /api/v1/auth/password/reset  → seteás el nuevo password
```

---

## Notas Importantes

- La cookie `pysessid` es **httponly** — JS no puede leerla. El browser la manda automaticamente.
- Para el resto de llamadas se usa `Authorization: Bearer <token>`.
- El register esta **deshabilitado** — es una app admin-only, los usuarios se crean via panel admin.
- Los permisos del usuario (`read:message`, `write:message`, `delete:message`) se controlan via el campo `permissions` en el rol.
- El token JWT expira en `jwt_expiry_minutes` (default 15 min). La session de la cookie dura 7 dias (o 90 con rememberMe).
