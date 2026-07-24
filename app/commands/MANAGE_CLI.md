# Manage CLI — Comandos de gestión

Sistema de comandos estilo Django para gestión de la aplicación.

## Uso general

```bash
uv run python app/manage.py <command> [args]
```

Sin argumentos muestra la ayuda con todos los comandos disponibles.

## Comandos incluidos

### migrate

Aplica todas las migraciones pendientes de Alembic a la base de datos.

```bash
uv run python app/manage.py migrate
```

### makemigrations

Genera una nueva migración a partir de los cambios detectados en los modelos.

```bash
uv run python app/manage.py makemigrations "descripcion del cambio"
```

El número de revisión se asigna automáticamente (incremental).

### create-admin

Crea un usuario administrador en la base de datos.

```bash
# Valores por defecto: admin@typecrafters.com / Admin123!
uv run python app/manage.py create-admin

# Con email y password custom
uv run python app/manage.py create-admin otro@email.com mi.password
```

### seed-legal-pages

Inserta o actualiza las páginas legales por defecto (privacy policy, terms of
service) con su contenido markdown. Idempotente: re-ejecutar actualiza el
contenido si cambió.

```bash
uv run python app/manage.py seed-legal-pages
```

### seed-messages

Inserta mensajes de contacto mock para testing.

```bash
uv run python app/manage.py seed-messages                # insertar todos
uv run python app/manage.py seed-messages --mark-read 3 # marcar los primeros 3 como leídos
uv run python app/manage.py seed-messages --clear       # borrar todos los mensajes antes de insertar
```

## Agregar un nuevo comando

1. Creá un archivo `.py` en `app/commands/`:

```python
# app/commands/seed.py

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.config.settings import settings


def _seed(args):
    engine = create_engine(settings.db_url)
    with Session(engine) as session:
        # tu lógica acá
        print("Datos insertados")


def register(registry):
    registry.add(
        name="seed",
        help="Insertar datos de prueba en la base de datos",
        fn=_seed,
    )
```

2. El comando se registra automáticamente al correr `manage.py`.

### Convenciones

- Cada comando es un archivo separado en `app/commands/`
- Todo archivo debe tener una función `register(registry)`
- La función principal recibe `args: list[str]` (los argumentos después del nombre del comando)
- Si el comando necesita args obligatorios, usar `min_args` en el registro
- Usar `raise SystemExit(codigo)` para indicar error (no `sys.exit()`)
- Los imports de la app van dentro de la función principal para no romper el autodiscovery

### Ejemplo con args obligatorios

```python
def _deploy(args):
    env = args[0]  # requerido
    print(f"Deploying to {env}")


def register(registry):
    registry.add(
        name="deploy",
        help="Deploy the application to an environment",
        fn=_deploy,
        min_args=1,  # falla si no se pasa al menos 1 argumento
    )
```
