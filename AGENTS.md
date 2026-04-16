# Project: LoreForge

## Overview
This is a python Django website with optional, modular applications to enable users to organize their TTRPG world and campaign lore, includine but not limited to: history, lore, factions, NPCs, locations, geography, maps, campaign frames, and more.

## Tech Stack
- Python 3.12+
- Django 5.x (Django ORM — no SQLAlchemy)
- PostgreSQL 16
- Gunicorn (WSGI server)
- Tailwind CSS + Leaflet.js (frontend)
## Commands
- Run dev: `docker-compose up` or `python manage.py runserver`
- Run tests: `pytest`
- Lint / type-check: `ruff check . && mypy .`
- Translations: `python manage.py makemessages -l en`

## Project Structure
```
apps/         Django apps (accounts, worlds, worldbook, npcs, timeline, maps, search, modules)
config/       Django settings (base, dev, prod), urls.py, wsgi.py
system_modules/  Pluggable TTRPG system modules (dnd5e, etc.)
templates/    HTML templates
static/       CSS, JS, images
media/        User uploads
locale/       i18n translation files
tests/        unit/, integration/, e2e/
docker/       Dockerfile, docker-compose.yml
docs/         Deployment guides
```

## Architecture
Browser → Gunicorn → Django middleware (auth, i18n) → URL router → View → Service layer → Django ORM → PostgreSQL → Template → HTML response.
Views are thin; business logic lives in `apps/*/services.py`.

## Code Patterns
- Naming: camelCase for variables/functions, PascalCase for classes/components, kebab-case for files
- Error handling: propagate errors to the caller; never silently swallow exceptions
- Imports: absolute imports from project root; no relative ../../ chains
## Testing Strategy
- Framework: pytest
- Unit tests: test individual functions and modules in isolation
- Integration tests: test API routes, DB interactions, service boundaries
- End-to-end: simulate real user flows through the full stack
- Run tests: `pytest`
- Always run tests before committing — never skip validation
## Commit Convention
Format: `[type]: [description]`
Types: feat, fix, refactor, test, docs, chore
Body: include what was built, key decisions, and anything future sessions should know.
## Sensitive Areas
Apply extra care and always request human review for: Authentication / authorization, Payments / billing, Data privacy / PII, Database migrations, Deployment / infrastructure
## On-Demand Context
When working on frontend components → read `reference/components.md`
When building API routes or endpoints → read `reference/api-patterns.md`
When designing or reviewing tests → read `reference/testing-strategy.md`
When working with the database or migrations → read `reference/database-patterns.md`

---
*Keep this file under 250 lines. Everything else lives in reference/ docs or commands.*
