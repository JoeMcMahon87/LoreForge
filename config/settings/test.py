"""
Test settings — uses SQLite so tests run without a PostgreSQL instance.
Switch DJANGO_SETTINGS_MODULE to config.settings.dev to run against a real DB.
"""
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable --reuse-db for in-memory SQLite (it's always fresh)
