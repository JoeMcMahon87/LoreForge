from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://loreforge:loreforge@localhost:5432/loreforge")
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
