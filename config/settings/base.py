"""
Base settings shared across all environments.
"""
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / "subdir"
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Read .env file if it exists
environ.Env.read_env(BASE_DIR / ".env")

# Security
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-in-production")

DEBUG = False

ALLOWED_HOSTS: list[str] = []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "apps.accounts",
    # Future apps (stubs — uncomment as phases are implemented)
    # "apps.worlds",
    # "apps.worldbook",
    # "apps.npcs",
    # "apps.timeline",
    # "apps.maps",
    # "apps.search",
    # "apps.modules",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Custom user model — must be set before first migrate
AUTH_USER_MODEL = "accounts.CustomUser"

# Auth redirects
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
USE_I18N = True
LANGUAGE_CODE = "en-us"
USE_TZ = True
TIME_ZONE = "UTC"
LOCALE_PATHS = [BASE_DIR / "locale"]

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = env("MEDIA_ROOT", default=str(BASE_DIR / "media"))

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
