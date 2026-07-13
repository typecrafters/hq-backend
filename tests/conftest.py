"""Pytest configuration — sets required env vars before any test imports."""

import os

# Set all required environment variables so the module-level Settings()
# instantiation in app.config.settings can succeed during test imports.
# These are test defaults; individual tests may override via monkeypatch.
os.environ.setdefault("DB_DRIVER", "psycopg")
os.environ.setdefault("DB_ENGINE", "postgresql")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASS", "test-password")
os.environ.setdefault("DB_NAME", "testdb")
os.environ.setdefault("SMTP_HOST", "")
os.environ.setdefault("SMTP_PORT", "0")
os.environ.setdefault("SMTP_USER", "")
os.environ.setdefault("SMTP_PASS", "")
os.environ.setdefault("SMTP_FROM", "")
os.environ.setdefault("S3_ENDPOINT", "")
os.environ.setdefault("S3_ACCESS_KEY", "")
os.environ.setdefault("S3_SECRET_KEY", "")
os.environ.setdefault("S3_SECURE", "false")
os.environ.setdefault("FRONTEND_URL", "http://localhost")
