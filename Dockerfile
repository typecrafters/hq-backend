# ==============================================================================
# Dockerfile — hq-backend (uv + uvicorn)
# ==============================================================================
# Multi-stage:
#   base         — creates /opt/venv and installs production dependencies
#   production   — copies source, runs uvicorn
#                  (docker compose --profile prod up)
#   development  — adds dev deps + watchdog, expects source mounted as volume,
#                  uvicorn --reload
#                  (docker compose --profile dev up)
# ==============================================================================

# ── base ─────────────────────────────────────────────────────────────────────
FROM python:3.14-slim AS base

# Copy the uv binary (avoids curl | sh patterns).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create the virtual environment OUTSIDE /app so a bind-mount of the project
# root at runtime doesn't shadow it.
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
# Prepend the venv bin directory to PATH so all subsequent RUN / CMD
# commands use the venv Python and its packages.
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install production dependencies.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --active

# ── production ───────────────────────────────────────────────────────────────
FROM base AS production

# Copy the full source tree (excluded files are handled by .dockerignore).
COPY . .

EXPOSE 8000
# Use the explicit venv path so Docker doesn't need to resolve $PATH.
CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── development (hot-reload) ─────────────────────────────────────────────────
FROM base AS development

# Add dev dependencies on top of the production ones.
RUN uv sync --frozen --all-groups --active

# Install watchdog for reliable file-watching in bind-mounted volumes
# (Docker Desktop on Windows/macOS doesn't propagate inotify events).
RUN uv pip install "watchdog>=6"

EXPOSE 8000
CMD ["/opt/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
