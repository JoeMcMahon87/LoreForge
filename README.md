# LoreForge

A system-agnostic TTRPG campaign management platform for Game Masters. LoreForge acts as a centralized command center for world-building and session play — from deep lore and living NPCs to interactive maps and in-session search.

---

## Overview

Game Masters accumulate vast amounts of campaign material across notebooks, wikis, and spreadsheets. Finding the right piece of lore mid-session breaks immersion and slows play. LoreForge consolidates everything into a single, structured, searchable hub that GMs can self-host or deploy to the cloud.

LoreForge is designed to be **system-agnostic** at its core, with a pluggable module system that adds game-specific functionality (stat blocks, campaign frames, adversary templates) for any TTRPG system.

### Who It's For

| Role | Description |
|---|---|
| **Game Master** | Primary user — builds worlds, manages campaigns, creates all lore entries |
| **Player** | Read-only access to lore and content the GM shares with them |
| **Admin** | Manages users and installed system modules |
| **Public** | Unauthenticated read-only access to publicly shared content |

---

## Objectives

### v1 Goals

- **Worldbook** — CRUD for Locations, Factions, Items, and Lore/History entries with per-entry visibility controls (GM-only, player-visible, public)
- **NPC Management** — Full NPC profiles with appearance, motivations, secrets, NPC-to-NPC relationships, and session appearance logs
- **Timeline** — Eras and events with entry linkage and visual display
- **Maps** — Uploaded image maps with pinned entry links, plus geospatial Leaflet.js maps for locations with lat/lng coordinates
- **Full-Text Search** — Fast, world-scoped search across all entries, NPCs, and events for use during live play
- **Plugin Module System** — Installable per-world modules that extend core models with system-specific fields; ships with a D&D 5e reference module
- **Accessibility** — WCAG 2.2 AA compliance across all pages
- **i18n Ready** — Full Django i18n scaffolding; English only in v1, additional language packs supported
- **Deployable** — Docker Compose for local/self-hosted use; documented AWS deployment path

### Out of Scope (v1)

- VTT integrations (Foundry VTT, Roll20, etc.)
- Encounter builder / loot generator
- AI-assisted content generation
- Real-time collaboration
- Mobile native app

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web Framework | Django 5.x |
| WSGI Server | Gunicorn |
| Database | PostgreSQL 16 |
| ORM | Django ORM |
| Frontend | Django/Jinja templates + Tailwind CSS |
| Maps | Leaflet.js |
| Rich Text | django-prose-editor |
| File Storage | Local filesystem (dev) / S3-compatible (prod) |
| Search | PostgreSQL full-text search |
| Containerisation | Docker + Docker Compose |

---

## Project Structure

```
loreforge/
├── apps/                    # Django applications
│   ├── accounts/            # User model, roles, auth
│   ├── worlds/              # World and Campaign models
│   ├── worldbook/           # Entry types: Location, Faction, Item, Lore
│   ├── npcs/                # NPC profiles, relationships, session logs
│   ├── timeline/            # Eras and timeline events
│   ├── maps/                # Image maps, pins, geospatial views
│   ├── search/              # Full-text search
│   └── modules/             # Plugin system registry and loader
├── system_modules/          # Pluggable TTRPG system modules
│   ├── base/                # Abstract interfaces
│   └── dnd5e/               # D&D 5e reference module
├── config/                  # Django settings (base/dev/prod), urls, wsgi
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── media/                   # User-uploaded files
├── locale/                  # i18n translation files
├── tests/                   # unit/, integration/, e2e/
├── docker/                  # Dockerfile, docker-compose files
└── docs/                    # Deployment guides
```

---

## Quick Start (Local)

### Prerequisites

- Docker and Docker Compose
- Git

### Run with Docker

```bash
git clone <repo-url> loreforge
cd loreforge
cp .env.example .env          # edit as needed
docker-compose up --build
```

The app will be available at `http://localhost:8000`.

### Run without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt

cp .env.example .env          # set DATABASE_URL, SECRET_KEY, etc.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Development

```bash
# Run tests
pytest

# Lint and type-check
ruff check . && mypy .

# Generate translation strings
python manage.py makemessages -l en

# Compile translations
python manage.py compilemessages
```

---

## Deployment

See [`docs/aws-deployment.md`](docs/aws-deployment.md) for the AWS EC2/ECS + RDS deployment guide.  
See [`docs/self-hosting.md`](docs/self-hosting.md) for self-hosted Docker Compose setup.

---

## Plugin Modules

LoreForge supports installable system modules that add TTRPG-specific functionality to a world without modifying core models. A module can contribute:

- Extended model fields (e.g. stat blocks on NPCs)
- Additional entry types
- Custom templates injected into entry detail pages

The **D&D 5e module** ships as a reference implementation. Community modules live in `system_modules/`.

---

## License

TBD
