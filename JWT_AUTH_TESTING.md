# JWT Auth — Guía de testing

## Setup

```bash
# 1. Crear .env con JWT_SECRET
echo "JWT_SECRET=una-clave-segura-de-al-menos-32-caracteres" >> .env

# 2. Arrancar el server
uv run uvicorn app.main:app --reload
```

## Endpoints

### 1. Registro (crear usuario nuevo)

```bash
curl -v -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane@example.com", "password": "secure123"}'
```

**Respuesta exitosa (201):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```
**Cookie:** `pysessid=<hex>` (Set-Cookie header)

**409** → `{"detail": "Email already registered."}`

---

### 2. Login

```bash
curl -v -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "jane@example.com", "password": "secure123", "rememberMe": false}'
```

**Respuesta exitosa:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```
**Cookie:** `pysessid=<hex>` (Set-Cookie header)

**401** → `{"detail": "Unauthorized."}` (email o password incorrecto)

---

### 3. Llamar ruta protegida con el token

```bash
curl -v "http://localhost:8000/v1/users/?page=1&limit=10" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**200** → devuelve usuarios · **401** → token inválido/expirado

---

### 4. Refrescar token (usando cookie)

```bash
# El browser manda la cookie sola, pero en curl:
curl -v -X POST http://localhost:8000/v1/auth/refresh \
  -b "pysessid=abc123..." \
  -H "User-Agent: curl/8.0"
```

Respuesta:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "tokenType": "bearer",
  "expiresIn": 900
}
```

**401** → sesión inválida, expirada o revocada

---

### 5. Logout

```bash
curl -v -X POST http://localhost:8000/v1/auth/logout \
  -b "pysessid=abc123..."
```

**204** → session revocada, cookie limpiada

---

### 6. Tests automatizados

```bash
# Todo el suite
uv run pytest -v

# Solo tests de auth
uv run pytest -v -k "jwt or auth"
```

---

## Flujo completo para probar (SPA / mobile)

```
1. POST /auth/register        → creás cuenta, recibís accessToken + cookie pysessid
2. GET  /users con Bearer     → usás accessToken del paso 1
3. Cuando el token expira (15 min):
   POST /auth/refresh         → el browser manda la cookie, recibís nuevo accessToken
4. POST /auth/logout          → el browser manda la cookie, se revoca la sesión
```

**Importante:** la cookie `pysessid` es `httponly` — JS no puede leerla. El browser la manda automáticamente en `/auth/refresh` y `/auth/logout`. Para el resto de las llamadas usás `Authorization: Bearer <token>`.
