# PRD — LoreForge
*Last updated: 2026-04-16*

---

## 1. Problem Statement

Game Masters running tabletop RPG campaigns accumulate enormous amounts of world-building material — NPCs, locations, factions, histories, maps, session notes — spread across notebooks, wikis, spreadsheets, and sticky notes. Finding the right piece of lore mid-session breaks immersion and slows play. No existing tool gives GMs a single, fast, structured hub that is **system-agnostic**, **self-hostable**, and extensible with **TTRPG-system-specific modules**.

**Who it's for:**
- **GMs** — primary power users building and running campaigns
- **Players** — consume curated lore their GM shares with them
- **Admins** — manage users and installed system modules
- **Public visitors** — read-only access to content a GM explicitly makes public

---

## 2. MVP Scope (v1)

The minimum feature set for a working, useful v1:

| Feature | Description |
|---|---|
| **Auth & Roles** | Registration, login, logout. Roles: admin, GM, player, public (unauthenticated). |
| **Worlds & Campaigns** | GMs create one or more worlds; each world has one or more campaigns. |
| **Worldbook Entries** | CRUD for Locations, Factions, Items, and Lore/History entries. Per-entry visibility (GM-only, player, public). Rich text content. |
| **NPC Management** | Full NPC records: appearance, motivations, secrets. NPC-to-NPC relationships. Session appearance logs. |
| **Timeline** | Eras and events, each event linkable to entries. Visual timeline display. |
| **Maps** | (a) Uploaded image maps with drag-and-drop pins linked to entries. (b) Geospatial map view (Leaflet.js) for locations with lat/lng coordinates. |
| **Full-Text Search** | Fast search across all worldbook entries, NPCs, and timeline events within a world. |
| **Plugin Module System** | Installable per-world modules that extend entries with system-specific fields (e.g. stat blocks). Ships with a D&D 5e reference module. |
| **i18n Scaffolding** | Django's i18n infrastructure wired up; all strings translation-ready. English only in v1. |
| **WCAG 2.2 Compliance** | AA level accessibility across all templates. |
| **Local + AWS Deployable** | Docker Compose for local dev/self-hosting; documented AWS path (EC2/ECS + RDS). |

---

## 3. Out of Scope (v1)

- VTT integrations (Foundry VTT, Roll20, etc.)
- Encounter builder / loot generator
- AI-assisted content generation
- Entry version history / audit log
- Real-time collaboration (websockets)
- Mobile native app
- Billing / subscriptions
- Languages other than English (infrastructure only)
- Daggerheart module (D&D 5e ships as reference; others are community-built)

---

## 4. Tech Stack

| Layer | Choice | Rationale |
|---|---|---|
| **Language** | Python 3.12+ | Team familiarity, Django ecosystem |
| **Web framework** | Django 5.x | Batteries-included admin, ORM, auth, i18n, forms |
| **WSGI server** | Gunicorn | Production-grade, standard Django deployment |
| **ORM** | Django ORM | Ships with Django; PostGIS extension for geospatial |
| **Database** | PostgreSQL 16 | Full-text search, PostGIS, JSONB for module fields |
| **Frontend** | Django templates + Jinja2 | Server-rendered; no SPA build pipeline |
| **CSS** | Tailwind CSS (CDN for v1) | Utility-first; accessible component patterns |
| **Maps** | Leaflet.js | Open-source, no API key required, flexible |
| **Rich text** | django-prose-editor (or django-ckeditor) | In-template WYSIWYG |
| **File storage** | Local filesystem (dev) / S3-compatible (prod) | django-storages handles both |
| **Search** | PostgreSQL full-text search via Django | No extra service in v1; upgrade to Meilisearch later |
| **Testing** | pytest + pytest-django | Per AGENTS.md |
| **Containerisation** | Docker + Docker Compose | Local dev and self-hosting |
| **Deployment** | AWS EC2 or ECS + RDS PostgreSQL | Standard, well-documented path |

> **AGENTS.md correction**: SQLAlchemy and `uvicorn` references in the existing AGENTS.md are incorrect for this stack. AGENTS.md will be updated as part of Phase 1.

---

## 5. Directory Structure

```
loreforge/
├── manage.py
├── gunicorn.conf.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/                        # Django project package
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                          # All Django apps live here
│   ├── accounts/                  # User model, roles, auth views
│   ├── worlds/                    # World + Campaign models
│   ├── worldbook/                 # Entry base + Location, Faction, Item, Lore
│   ├── npcs/                      # NPC model, relationships, session logs
│   ├── timeline/                  # Era + Event models
│   ├── maps/                      # Image maps, pins, geospatial views
│   ├── search/                    # Full-text search views + indexes
│   └── modules/                   # Plugin system: registry, loader, base classes
├── system_modules/                # Installable TTRPG system modules
│   ├── base/                      # Abstract interfaces (StatBlock, etc.)
│   └── dnd5e/                     # D&D 5e reference module
├── templates/
│   ├── base.html
│   ├── partials/
│   ├── accounts/
│   ├── worlds/
│   ├── worldbook/
│   ├── npcs/
│   ├── timeline/
│   └── maps/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/                         # User-uploaded files (maps, images)
├── locale/                        # i18n .po / .mo files
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── scripts/                       # flush.py, hooks, etc.
├── plans/                         # PIV feature plans
├── knowledge/                     # KB articles and index
├── reference/                     # On-demand context docs
└── docs/                          # Deployment guides, AWS setup
```

---

## 6. Architecture

### 6.1 Request Flow

```
Browser → Gunicorn → Django middleware (auth, i18n) → URL router
       → View (class-based) → Service layer → Django ORM → PostgreSQL
       → Template → HTML response
```

- **Views** are thin: validate input, call service functions, render template.
- **Service layer** (`apps/*/services.py`) contains business logic; testable in isolation.
- **Models** handle data shape and DB constraints only.

### 6.2 Auth & Roles

| Role | Capabilities |
|---|---|
| `admin` | Full site access, user management, module installation |
| `gm` | Create/manage worlds, campaigns, all entries within their worlds |
| `player` | Read-only access to entries marked `visibility=player` in worlds they're invited to |
| `public` (anonymous) | Read-only access to entries marked `visibility=public` |

- Built on Django's `AbstractUser` + a `role` field.
- Per-object visibility controlled by `visibility` field on `Entry` model: `gm_only | player | public`.
- World membership tracked via `WorldMembership(user, world, role)` join table.

### 6.3 Core Database Schema

```
User
  id, email, username, role, created_at

World
  id, name, slug, description, owner(FK User), created_at

Campaign
  id, name, world(FK), description, status(active|complete|hiatus), created_at

WorldMembership
  id, user(FK), world(FK), role(gm|player)

Entry  [abstract base — concrete tables per type]
  id, title, slug, content(text), visibility, world(FK), created_by(FK),
  tags(M2M Tag), created_at, updated_at

Location(Entry)
  lat, lng, region, location_type, parent_location(FK self)

Faction(Entry)
  alignment, goals

Item(Entry)
  item_type, rarity

Lore(Entry)
  lore_type  [history | myth | legend | other]

NPC(Entry)
  appearance(text), motivations(text), secrets(text), status(alive|dead|unknown)

NPCRelationship
  npc_a(FK NPC), npc_b(FK NPC), relationship_type, description

SessionLog
  id, campaign(FK), session_number, session_date, summary

SessionAppearance
  session_log(FK), npc(FK), notes

Era
  id, name, world(FK), start_label, end_label, order

TimelineEvent
  id, name, era(FK), date_label, description, entries(M2M Entry)

MapImage
  id, world(FK), title, image(ImageField), created_at

MapPin
  id, map_image(FK), x_pct(float), y_pct(float), entry(FK Entry), label

InstalledModule
  id, world(FK), module_slug, version, config(JSONB)
```

### 6.4 Plugin Module System

- Each system module is a Python package under `system_modules/<slug>/`.
- Modules declare themselves via a `ModuleManifest` class: name, slug, version, entry_extensions.
- Modules can register **entry extension models** (e.g. `DnD5eStatBlock` with FK to `NPC`) that add system-specific fields without modifying core models.
- A `ModuleRegistry` (singleton, loaded at startup) discovers and validates installed modules.
- Per-world installation tracked in `InstalledModule`; modules can be enabled/disabled per world.

### 6.5 Maps Architecture

- **Image maps**: Upload PNG/JPG → stored via django-storages. Pins stored as `(x_pct, y_pct)` percentage coordinates so they survive image resizing. Rendered client-side with a lightweight JS overlay.
- **Geospatial maps**: `Location` entries with `lat`/`lng` rendered via Leaflet.js. No PostGIS in v1 (plain float fields); PostGIS can be added later for spatial queries.

### 6.6 Search

- PostgreSQL full-text search using Django's `SearchVector` / `SearchQuery`.
- Search index covers `Entry.title`, `Entry.content`, `NPC` fields, `TimelineEvent.name`.
- Scoped to a single world per query (no cross-world search in v1).
- `apps/search/` provides a single search view + service function.

### 6.7 i18n

- `USE_I18N = True` in all settings.
- All user-facing strings wrapped in `_()` / `{% trans %}`.
- `locale/` directory pre-created; `django-admin makemessages` ready to run.
- Language selection via URL prefix (`/en/`, `/fr/`) using `i18n_patterns`.

### 6.8 Deployment Targets

**Local / self-hosted:**
```
docker-compose up
  → postgres:16
  → loreforge (gunicorn, port 8000)
  → nginx (reverse proxy, static files)
```

**AWS (documented path):**
```
RDS PostgreSQL → EC2 (or ECS Fargate) running Docker image
              → S3 for media files (django-storages)
              → CloudFront optional (static assets)
```
Environment-specific config via `.env` file + `django-environ`.

---

## 7. Phases of Work

Each phase is a single PIV loop (half-day to one day). Dependencies noted.

### Phase 1 — Project Foundation
**Goal**: Runnable Django project, correct tooling, auth scaffolding.

- Initialize Django project in `loreforge/` with split settings (base/dev/prod)
- `User` model with `role` field (admin, gm, player)
- Login, logout, registration views + templates (WCAG 2.2 AA)
- Base template (`base.html`) with navigation skeleton, i18n wiring, Tailwind
- pytest + pytest-django configured; first smoke test passes
- Docker Compose (postgres + app + nginx)
- `gunicorn.conf.py`
- Update `AGENTS.md` to reflect correct stack (remove SQLAlchemy/uvicorn references)
- `.env.example` with all required vars

*Deliverable*: `docker-compose up` → login page loads; tests pass.

---

### Phase 2 — Worlds & Campaigns
**Goal**: GMs can create and manage worlds; player membership works.

- `World`, `Campaign`, `WorldMembership` models + migrations
- World CRUD views (GM-only create/edit/delete; player/public read)
- Campaign CRUD scoped to a world
- World dashboard page (hub for all world content)
- Role-based permission mixins (`GMMixin`, `WorldMemberMixin`)
- Tests: world creation, membership, permission enforcement

*Deliverable*: GM can create a world, invite a player; player sees world dashboard.

---

### Phase 3 — Worldbook Entries (Core)
**Goal**: CRUD for all four entry types with visibility controls.

- Abstract `Entry` base + concrete `Location`, `Faction`, `Item`, `Lore` models
- `Tag` model + M2M
- Per-entry visibility (`gm_only`, `player`, `public`)
- Generic entry list/detail/create/edit/delete views
- Entry type-specific forms and templates
- Visibility-filtered querysets in all list views
- Tests: CRUD, visibility filtering, slug uniqueness per world

*Deliverable*: GM can create all entry types; player sees only player-visible entries.

---

### Phase 4 — NPC Management
**Goal**: Full NPC records, relationships, session logs.

- `NPC`, `NPCRelationship`, `SessionLog`, `SessionAppearance` models
- NPC CRUD views + templates
- Relationship management UI (add/edit/remove NPC ↔ NPC links)
- Session log CRUD + NPC appearance tracking
- NPC detail page shows relationships and session history
- Tests: NPC CRUD, relationship creation, session log entries

*Deliverable*: GM can build NPC profiles, link them, and log which sessions they appeared in.

---

### Phase 5 — Timeline
**Goal**: Eras and events with entry linkage; visual display.

- `Era`, `TimelineEvent` models + migrations
- Event ↔ Entry M2M
- Timeline list/detail views
- Visual timeline template (CSS/JS, accessible)
- Event linked to entries surfaces on entry detail page
- Tests: era/event CRUD, entry linkage, ordering

*Deliverable*: GM can build a world timeline; clicking an event shows linked entries.

---

### Phase 6 — Maps
**Goal**: Both image maps (pinned) and geospatial (Leaflet).

- `MapImage`, `MapPin` models + migrations
- Image map upload (django-storages); pin CRUD via drag-and-drop JS overlay
- Pins link to `Entry` objects; clicking a pin navigates to entry
- `Location` entries with `lat`/`lng` rendered on a Leaflet world map
- Location map view (all world locations with lat/lng plotted)
- Tests: image upload, pin creation, location map query

*Deliverable*: GM can upload a map image and pin locations to it; separate view shows all geo-located entries on a Leaflet map.

---

### Phase 7 — Full-Text Search
**Goal**: Fast, scoped search during live play.

- `SearchVector` indexes on `Entry`, `NPC`, `TimelineEvent`
- Search view with query + optional type filter
- Results page with type badges and entry links
- Search bar in base template (always visible)
- Keyboard shortcut (e.g. `/` focuses search input) — WCAG compliant
- Tests: search returns correct results; scoped to current world; empty state handled

*Deliverable*: GM can search any entry by keyword during a session.

---

### Phase 8 — Plugin Module System
**Goal**: Installable per-world modules; D&D 5e reference module.

- `ModuleManifest` base class and `ModuleRegistry` loader
- `InstalledModule` model; admin UI to enable/disable per world
- Extension model pattern (module-owned models FK to core models)
- D&D 5e module: `DnD5eStatBlock` (FK to `NPC`) with standard 5e fields
- Module-contributed templates injected into NPC/entry detail pages
- Module management page (admin + GM)
- Tests: module discovery, install/uninstall, stat block CRUD, template injection

*Deliverable*: GM installs D&D 5e module on a world; NPCs show stat block section.

---

### Phase 9 — Polish, Accessibility Audit & Deployment Docs
**Goal**: Ship-ready v1.

- Full WCAG 2.2 AA audit + fixes (axe-core / manual keyboard nav check)
- AWS deployment guide in `docs/aws-deployment.md`
- `docker-compose.prod.yml` with S3 media, environment hardening
- `docs/self-hosting.md` quickstart guide
- End-to-end test: GM creates world → adds entries → searches → installs module
- Performance: add `select_related`/`prefetch_related` on any N+1 queries found
- Final `AGENTS.md` + `reference/` doc updates

*Deliverable*: Documented, accessible, deployable v1.

---

## Appendix A: Roles & Permissions Matrix

| Action | public | player | gm | admin |
|---|---|---|---|---|
| View public entries | ✓ | ✓ | ✓ | ✓ |
| View player entries | — | ✓ (member) | ✓ | ✓ |
| View GM-only entries | — | — | ✓ (owner) | ✓ |
| Create/edit entries | — | — | ✓ | ✓ |
| Create world | — | — | ✓ | ✓ |
| Invite players | — | — | ✓ (owner) | ✓ |
| Install modules | — | — | ✓ (owner) | ✓ |
| Manage users | — | — | — | ✓ |

---

## Appendix B: Environment Variables

```
DJANGO_SECRET_KEY=
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=
DATABASE_URL=postgres://user:pass@host:5432/loreforge
MEDIA_ROOT=/app/media          # local
AWS_STORAGE_BUCKET_NAME=       # prod
AWS_ACCESS_KEY_ID=             # prod
AWS_SECRET_ACCESS_KEY=         # prod
DEFAULT_FROM_EMAIL=
```
