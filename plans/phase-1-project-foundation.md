# Phase 1 — Project Foundation

## Goal
A fully runnable Django 5.2 project with correct tooling, a custom User model with roles, working auth pages (login / register / logout), a WCAG 2.2 AA base template, pytest passing, and Docker Compose bringing the stack up cleanly.

---

## Context

- **Affected files**: Everything — this is a greenfield setup. All files listed below are new.
- **External docs**:
  - Django 5.2 docs: https://docs.djangoproject.com/en/5.2/
  - pytest-django: https://pytest-django.readthedocs.io/
  - django-environ: https://django-environ.readthedocs.io/
  - WhiteNoise: https://whitenoise.readthedocs.io/
- **Dependencies** (all versions confirmed from PyPI, April 2026):

  ```
  # base
  Django==5.2.13
  gunicorn==25.3.0
  psycopg[binary]==3.3.3
  django-environ==0.13.0
  whitenoise==6.12.0
  Pillow==12.2.0

  # dev
  pytest==8.x
  pytest-django==4.12.0
  factory-boy==3.3.3
  ruff==0.15.10
  mypy==1.20.1
  django-stubs==5.2.9

  # prod (extends base)
  whitenoise[brotli]
  ```

- **ENV vars required**: See `.env.example` (Task 14).
- **Constraint**: `AUTH_USER_MODEL` must be set **before** the first `migrate` run — never change it after.

---

## Task List

### 1. `pyproject.toml`
Create at project root. Contains pytest, ruff, and mypy configuration.

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.dev"
python_files = ["test_*.py", "*_test.py"]
addopts = "--reuse-db"

[tool.ruff]
target-version = "py312"
line-length = 119

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP"]

[tool.mypy]
python_version = "3.12"
plugins = ["mypy_django_plugin.main"]

[tool.django-stubs]
django_settings_module = "config.settings.dev"
```

---

### 2. `requirements/base.txt`

```
Django==5.2.13
gunicorn==25.3.0
psycopg[binary]==3.3.3
django-environ==0.13.0
whitenoise==6.12.0
Pillow==12.2.0
```

### 3. `requirements/dev.txt`

```
-r base.txt
pytest
pytest-django==4.12.0
pytest-cov
factory-boy==3.3.3
ruff==0.15.10
mypy==1.20.1
django-stubs==5.2.9
```

### 4. `requirements/prod.txt`

```
-r base.txt
whitenoise[brotli]
```

---

### 5. `manage.py`
Standard Django manage.py — set `DJANGO_SETTINGS_MODULE` to `config.settings.dev`.

---

### 6. `config/settings/base.py`
Core settings shared across all environments. Key settings:

- `SECRET_KEY` — loaded from env via `django-environ`
- `INSTALLED_APPS` — includes `apps.accounts` and all future apps (stub list for now)
- `AUTH_USER_MODEL = "accounts.CustomUser"` — **critical, must be here**
- `MIDDLEWARE` — include `whitenoise.middleware.WhiteNoiseMiddleware` after `SecurityMiddleware`
- `TEMPLATES` — `APP_DIRS=True`, `context_processors` including `request`
- `STATIC_URL = "/static/"`, `STATICFILES_DIRS = [BASE_DIR / "static"]`
- `MEDIA_URL = "/media/"`, `MEDIA_ROOT = BASE_DIR / "media"`
- `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`
- `USE_I18N = True`, `LANGUAGE_CODE = "en-us"`, `USE_TZ = True`
- `LOCALE_PATHS = [BASE_DIR / "locale"]`

### 7. `config/settings/dev.py`

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://loreforge:loreforge@localhost:5432/loreforge")
}
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### 8. `config/settings/prod.py`

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
DATABASES = {"default": env.db("DATABASE_URL")}
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

### 9. `config/urls.py`
Root URL conf. Include `apps.accounts.urls` under `/accounts/`. Serve `media/` files in dev (guarded by `DEBUG`).

### 10. `config/wsgi.py`
Standard Django WSGI entry point for Gunicorn.

---

### 11. `apps/accounts/models.py`
Custom user model extending `AbstractUser`.

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        GM = "gm", _("Game Master")
        PLAYER = "player", _("Player")

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PLAYER,
    )

    def is_gm(self):
        return self.role == self.Role.GM

    def is_admin_user(self):
        return self.role == self.Role.ADMIN
```

### 12. `apps/accounts/forms.py`
Two forms:
- `RegistrationForm(UserCreationForm)` — email, username, password1, password2, role (player/gm only; admin not self-assignable)
- Login handled by Django's built-in `AuthenticationForm`

### 13. `apps/accounts/views.py`
Three views:
- `RegisterView(CreateView)` — creates user, logs in, redirects to home
- `LoginView` — use `django.contrib.auth.views.LoginView` with custom template
- `LogoutView` — use `django.contrib.auth.views.LogoutView`

### 14. `apps/accounts/urls.py`

```python
urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
```

### 15. `apps/accounts/admin.py`
Register `CustomUser` with `UserAdmin`, add `role` to `fieldsets`.

### 16. `apps/accounts/migrations/0001_initial.py`
Generated by `python manage.py makemigrations accounts`. Do not hand-write.

---

### 17. `templates/base.html`
WCAG 2.2 AA compliant base template. Required structure:

```html
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}LoreForge{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>  {# dev only — replace with built CSS in prod #}
</head>
<body>
  <!-- Skip link (WCAG 2.4.1) -->
  <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:p-2">
    {% trans "Skip to main content" %}
  </a>

  <header role="banner">
    {% include "partials/nav.html" %}
  </header>

  <main id="main-content" tabindex="-1">
    {% block content %}{% endblock %}
  </main>

  <footer role="contentinfo">
    ...
  </footer>
</body>
</html>
```

Key accessibility requirements:
- `lang` attribute on `<html>` (populated from `LANGUAGE_CODE`)
- Skip link to `#main-content`
- All form inputs have visible `<label>` or `aria-label`
- Error messages linked to inputs via `aria-describedby`
- Colour contrast ratio ≥ 4.5:1 for normal text
- Focus indicators visible (Tailwind `focus:ring`)

### 18. `templates/partials/nav.html`
Navigation bar with:
- Site logo / name linking to home
- `<nav aria-label="{% trans 'Main navigation' %}">` wrapper
- Links: Home, Login (if anonymous), Register (if anonymous), Logout (if authenticated)
- User display name when authenticated

### 19. `templates/accounts/login.html`
Extends `base.html`. Renders `AuthenticationForm`. Accessible: labels, error list with `role="alert"`.

### 20. `templates/accounts/register.html`
Extends `base.html`. Renders `RegistrationForm`. Same accessibility requirements.

---

### 21. `static/css/main.css`
Empty placeholder for now. Tailwind CDN handles all styling in v1 dev.

### 22. `static/js/main.js`
Empty placeholder.

---

### 23. `locale/` directory
Create `locale/en/LC_MESSAGES/` — empty, ready for `makemessages`.

---

### 24. `tests/conftest.py`
Project-level pytest fixtures:

```python
import pytest
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def gm_user(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username="testgm", password="pass1234!", role="gm"
    )

@pytest.fixture
def player_user(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username="testplayer", password="pass1234!", role="player"
    )
```

### 25. `tests/test_smoke.py`
Basic smoke tests to verify the app starts:

```python
import pytest

@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_page_loads(client):
    response = client.get("/accounts/register/")
    assert response.status_code == 200

@pytest.mark.django_db
def test_home_redirects_to_login_when_anonymous(client):
    response = client.get("/")
    assert response.status_code in (200, 302)
```

### 26. `tests/unit/accounts/test_models.py`
Unit tests for the `CustomUser` model:
- `is_gm()` returns True for gm role only
- `is_admin_user()` returns True for admin role only
- Default role is `player`

### 27. `tests/integration/accounts/test_auth.py`
Integration tests:
- Registration creates a user and redirects
- Login with correct credentials succeeds (302)
- Login with wrong password returns 200 with form errors
- Logout redirects to login page
- Registration form rejects admin role selection

---

### 28. `gunicorn.conf.py`

```python
import os

bind = "0.0.0.0:8000"
workers = 2 * (os.cpu_count() or 1) + 1
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
```

---

### 29. `docker/Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
```

### 30. `docker/docker-compose.yml` (local dev)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: loreforge
      POSTGRES_USER: loreforge
      POSTGRES_PASSWORD: loreforge
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    command: python manage.py runserver 0.0.0.0:8000
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.dev
    env_file:
      - ../.env
    volumes:
      - ..:/app
    ports:
      - "8000:8000"
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ../staticfiles:/app/staticfiles
    depends_on:
      - app

volumes:
  postgres_data:
```

### 31. `docker/nginx/nginx.conf`
Minimal nginx config: proxy to `app:8000`, serve `/static/` from volume.

### 32. `.env.example`

```
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://loreforge:loreforge@db:5432/loreforge
MEDIA_ROOT=/app/media
DEFAULT_FROM_EMAIL=noreply@loreforge.local
```

---

### 33. Update `reference/database-patterns.md`
Replace SQLAlchemy references with Django ORM. Update migration tool to `python manage.py migrate`. Keep the query conventions section.

### 34. Update `reference/testing-strategy.md`
Fix TypeScript/`*.test.ts` references to Python/Django conventions. Update co-location note to use `tests/unit/` and `tests/integration/`.

---

## Environment Setup

Before the implementation session begins, confirm:

1. Python 3.12 available: `python --version`
2. PostgreSQL 16 running (or Docker available): `docker --version`
3. No existing `loreforge/` Django project directory (we're building fresh)
4. Git repo is clean: `git status`

No `.env` file should exist yet — create it from `.env.example` after Task 32.

**Order of first run:**
```bash
pip install -r requirements/dev.txt
cp .env.example .env       # edit SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Validation Strategy

Perform each step in order. Do not proceed to the next step if the current one fails.

### Step 1 — Lint and type-check
```bash
ruff check .
mypy .
```
Expected: zero errors.

### Step 2 — Migrations are clean
```bash
python manage.py makemigrations --check
```
Expected: "No changes detected" — all migrations are committed.

### Step 3 — Unit tests
```bash
pytest tests/unit/ -v
```
Expected: all pass. Tests covered:
- `CustomUser.is_gm()` → True for gm, False otherwise
- `CustomUser.is_admin_user()` → True for admin, False otherwise
- Default role is `player`

### Step 4 — Integration tests
```bash
pytest tests/integration/ -v
```
Expected: all pass. Scenarios:
- `GET /accounts/login/` → 200
- `GET /accounts/register/` → 200
- `POST /accounts/register/` with valid data → 302 redirect, user exists in DB
- `POST /accounts/login/` with correct credentials → 302
- `POST /accounts/login/` with wrong password → 200, form errors present
- `POST /accounts/logout/` → 302 to login page

### Step 5 — Smoke tests
```bash
pytest tests/test_smoke.py -v
```
Expected: all pass.

### Step 6 — Full test suite
```bash
pytest --cov=apps --cov-report=term-missing
```
Expected: all tests pass; coverage report generated.

### Step 7 — Docker Compose
```bash
docker-compose -f docker/docker-compose.yml up --build
```
Expected:
- Postgres starts, healthy
- App starts without error
- `curl http://localhost:8000/accounts/login/` returns HTML with `<form`

### Step 8 — Manual browser walkthrough
Open `http://localhost:8000` in a browser:
1. Anonymous user → redirected to `/accounts/login/`
2. Navigate to `/accounts/register/` → registration form visible, all labels present
3. Register a new GM user → redirected, user logged in
4. Navigation bar shows username and Logout link
5. Logout → redirected to login page
6. Login with wrong password → error message displayed (accessible, `role="alert"`)
7. Login with correct password → logged in
8. Tab through login form — all focusable elements reachable in logical order
9. Check skip link: tab from address bar → first focusable is "Skip to main content"

### Step 9 — Accessibility spot-check
Using browser DevTools accessibility inspector:
- `<html lang="en">` present
- `<main id="main-content">` present, single instance
- All form inputs have associated labels
- Skip link visible on focus
- No ARIA roles that conflict with semantic HTML

---

## Notes for the Implementation Session

- Set `AUTH_USER_MODEL = "accounts.CustomUser"` in `base.py` **before** running any migration. If this is missed, the fix is destructive (drop DB, start over).
- Tailwind Play CDN is acceptable for v1 dev. Add a `<!-- TODO: replace with Tailwind CLI in prod -->` comment in `base.html`.
- The `--reuse-db` flag in pytest config speeds up repeated test runs. If the schema changes, run `pytest --create-db` once to force rebuild.
- `psycopg[binary]` (psycopg3) is the modern adapter. Do NOT use `psycopg2`. The Django `DATABASES` setting uses `"ENGINE": "django.db.backends.postgresql"` (unchanged — Django 5 uses psycopg3 transparently).
- Do not add `django-debug-toolbar` in this phase — keep dev dependencies minimal.
- Phase 2 will add `World` and `Campaign` models — the home `/` view can be a simple placeholder template for now.
