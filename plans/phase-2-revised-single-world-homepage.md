# Plan: Phase 2 Revised — Single-World Config, Campaigns & Configurable Homepage

*Created: 2026-04-20*

---

## Goal

Refactor the existing multi-world Phase 2 code to match the revised single-world PRD: one `WorldConfig` singleton per instance, standalone `Campaign` records, and a configurable homepage built from ordered, visibility-controlled widgets.

---

## Context

### Why this is a full rewrite of Phase 2 code

The original Phase 2 was implemented for a multi-world hosting model (`World`, `WorldMembership`, per-world URL scoping). The PRD was updated this session to a single-world instance model. All of the existing Phase 2 code in `apps/worlds/` reflects the old design and must be replaced.

### What already exists (must be changed or removed)

| File | Status |
|---|---|
| `apps/worlds/models.py` | Replace: remove `World`, `WorldMembership`; add `WorldConfig`; strip `world` FK from `Campaign` |
| `apps/worlds/views.py` | Replace: remove World CRUD; add `WorldConfigUpdateView`; fix Campaign views (no world slug) |
| `apps/worlds/forms.py` | Update: remove `WorldForm`; add `WorldConfigForm` |
| `apps/worlds/mixins.py` | Simplify: remove `WorldOwnerMixin`, `WorldMemberMixin`; keep `GMMixin` (unchanged) |
| `apps/worlds/services.py` | Replace: remove world/membership services; add world config + campaign services |
| `apps/worlds/urls.py` | Replace: new URL structure without world slug prefix |
| `apps/worlds/migrations/0001_initial.py` | Squash: rewrite to match new schema |
| `apps/home/models.py` | Extend: add `HomePageWidget` model; add `logo`/`theme_color` to `SiteConfig` |
| `apps/home/views.py` | Extend: add homepage editor views |
| `apps/home/migrations/0001_initial.py` | Migration 0002 adds new fields and `HomePageWidget` |
| `templates/worlds/world_list.html` | Delete |
| `templates/worlds/world_detail.html` | Delete |
| `templates/worlds/world_form.html` | Replace with `world_settings.html` |
| `templates/worlds/world_confirm_delete.html` | Delete |
| `templates/worlds/campaign_*.html` | Update: remove world-scoped breadcrumbs, fix URLs |
| `templates/home/home.html` | Replace: widget-driven rendering |
| `tests/unit/worlds/test_models.py` | Rewrite: WorldConfig singleton + Campaign tests |
| `tests/unit/worlds/test_services.py` | Rewrite: WorldConfig + Campaign services |
| `tests/integration/worlds/test_worlds.py` | Rewrite: WorldConfig settings view |
| `tests/integration/worlds/test_campaigns.py` | Rewrite: new URLs, no world_slug |
| `tests/integration/worlds/test_membership.py` | Delete: WorldMembership is gone |
| `tests/conftest.py` | Update: replace `world`/`player_member` fixtures |

### New files to create

| File | Purpose |
|---|---|
| `apps/home/registry.py` | Widget registry: maps `widget_type` slug → widget class |
| `apps/home/widgets.py` | Core widget class definitions (RichText, CampaignList, RecentEntries, ImageBanner) |
| `apps/home/widget_forms.py` | Config form per widget type |
| `templates/home/homepage_editor.html` | Homepage editor UI |
| `templates/home/widgets/rich_text.html` | Widget partial |
| `templates/home/widgets/campaign_list.html` | Widget partial |
| `templates/home/widgets/recent_entries.html` | Widget partial |
| `templates/home/widgets/image_banner.html` | Widget partial |
| `tests/unit/home/test_registry.py` | Widget registry unit tests |
| `tests/integration/home/test_homepage_editor.py` | Homepage editor integration tests |

### Affected URLs (before → after)

| Before | After |
|---|---|
| `GET /worlds/` | removed |
| `GET /worlds/create/` | removed |
| `GET /worlds/<world_slug>/` | removed |
| `GET /worlds/<world_slug>/edit/` | `GET /world/settings/` |
| `GET /worlds/<world_slug>/campaigns/create/` | `GET /campaigns/create/` |
| `GET /worlds/<world_slug>/campaigns/<c_slug>/` | `GET /campaigns/<c_slug>/` |
| `GET /worlds/<world_slug>/campaigns/<c_slug>/edit/` | `GET /campaigns/<c_slug>/edit/` |
| `GET /worlds/<world_slug>/campaigns/<c_slug>/delete/` | `GET /campaigns/<c_slug>/delete/` |
| *(new)* | `GET /homepage/edit/` |
| *(new)* | `POST /homepage/widgets/add/` |
| *(new)* | `GET/POST /homepage/widgets/<id>/edit/` |
| *(new)* | `POST /homepage/widgets/<id>/delete/` |
| *(new)* | `POST /homepage/widgets/<id>/move/` |

---

## External Docs to Reference

- Django `JSONField` docs: https://docs.djangoproject.com/en/5.2/ref/models/fields/#jsonfield
- Django singleton pattern: use `get_or_create(pk=1)` (already in codebase as `SiteConfig.get_solo()`)
- Tailwind drag-and-drop: not needed — use server-rendered up/down buttons for Phase 2

---

## Dependencies / Environment

- No new packages required for Phase 2 (JSONField is built into Django 5.x; works on both SQLite and PostgreSQL)
- No new env vars

---

## Task List

### Step 1 — Squash `apps/worlds` migrations to clean schema

1. Delete `apps/worlds/migrations/0001_initial.py`
2. Write new `apps/worlds/migrations/0001_initial.py` with only:
   - `WorldConfig` singleton (name, tagline, description, theme_color, logo)
   - `Campaign` with `slug` globally unique (no world FK)
3. Run `python manage.py migrate --run-syncdb` in dev to verify

**WorldConfig model (new):**
```python
class WorldConfig(models.Model):
    name = models.CharField(max_length=200, default="My World")
    tagline = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    theme_color = models.CharField(max_length=7, default="#4f46e5")  # hex
    logo = models.ImageField(upload_to="world/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "World Configuration"

    @classmethod
    def get_solo(cls) -> "WorldConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

**Campaign model (updated — no world FK):**
```python
class Campaign(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)  # globally unique now
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    # slug collision loop uses Campaign.objects.filter(slug=...) with no world scoping
```

### Step 2 — Simplify `apps/worlds/mixins.py`

- Remove `WorldOwnerMixin` and `WorldMemberMixin` entirely
- Keep `GMMixin` unchanged (it only checks `user.role` — still valid)
- Remove the `WorldMembership` import

### Step 3 — Rewrite `apps/worlds/services.py`

Remove all world/membership functions. Add:
```python
def get_world_config() -> WorldConfig:
    return WorldConfig.get_solo()

def update_world_config(name, tagline, description, theme_color, logo=None) -> WorldConfig:
    config = WorldConfig.get_solo()
    # update fields, save, return

def get_all_campaigns() -> QuerySet:
    return Campaign.objects.order_by("created_at")

def create_campaign(name, description="") -> Campaign:
    return Campaign.objects.create(name=name, description=description)
```

### Step 4 — Rewrite `apps/worlds/forms.py`

- Remove `WorldForm`
- Add `WorldConfigForm` (fields: name, tagline, description, theme_color, logo)
- Keep `CampaignForm` (remove world context; status stays `required=False`)

### Step 5 — Rewrite `apps/worlds/views.py`

Remove all World CRUD views. Replace with:

- `WorldConfigUpdateView(GMMixin, UpdateView)` — singleton edit, success_url → `world-settings`
- `CampaignListView(LoginRequiredMixin, ListView)` — all campaigns
- `CampaignCreateView(GMMixin, CreateView)` — no world FK injection
- `CampaignDetailView(LoginRequiredMixin, DetailView)` — lookup by `campaign_slug`
- `CampaignUpdateView(GMMixin, UpdateView)` — lookup by `campaign_slug`
- `CampaignDeleteView(GMMixin, DeleteView)` — success_url → `campaign-list`

Note: `WorldConfigUpdateView` needs a custom `get_object()` that returns `WorldConfig.get_solo()` rather than looking up by PK in URL.

### Step 6 — Rewrite `apps/worlds/urls.py`

```python
urlpatterns = [
    path("settings/", views.WorldConfigUpdateView.as_view(), name="world-settings"),
    path("campaigns/", views.CampaignListView.as_view(), name="campaign-list"),
    path("campaigns/create/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path("campaigns/<slug:campaign_slug>/", views.CampaignDetailView.as_view(), name="campaign-detail"),
    path("campaigns/<slug:campaign_slug>/edit/", views.CampaignUpdateView.as_view(), name="campaign-update"),
    path("campaigns/<slug:campaign_slug>/delete/", views.CampaignDeleteView.as_view(), name="campaign-delete"),
]
```

Update `config/urls.py` to mount worlds at `/world/` (singular) instead of `/worlds/`.

### Step 7 — Update `apps/worlds/admin.py`

Register `WorldConfig` and `Campaign`. Unregister `World` and `WorldMembership`.

### Step 8 — Add `HomePageWidget` model to `apps/home/models.py`

```python
class HomePageWidget(models.Model):
    class Visibility(models.TextChoices):
        GM_ONLY = "gm_only", _("GM only")
        PLAYER = "player", _("Player")
        PUBLIC = "public", _("Public")

    widget_type = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC)

    class Meta:
        ordering = ["order"]
```

Also add `logo` and `theme_color` fields to `SiteConfig` via migration 0002.

### Step 9 — Create widget registry (`apps/home/registry.py` and `apps/home/widgets.py`)

Each widget type is a Python class with:
- `type_slug: str` — unique identifier stored in `HomePageWidget.widget_type`
- `label: str` — shown in the picker UI
- `template_name: str` — partial template path
- `config_form_class` — form class for editing config (or `None`)
- `get_context(config: dict) -> dict` — returns template context from stored config

Core widget types for Phase 2:
- `RichTextWidget` — config: `{"content": "<html>"}`, no dynamic query
- `CampaignListWidget` — config: `{}`, queries `Campaign.objects.all()`
- `RecentEntriesWidget` — config: `{"count": 5}`, returns empty list (entries built in Phase 3)
- `ImageBannerWidget` — config: `{"image_url": "", "alt": "", "caption": ""}`

Registry is a simple module-level dict populated at import time. `ModuleRegistry` (Phase 8) will add to it.

### Step 10 — Add homepage editor views to `apps/home/views.py`

- `HomeView` — unchanged except widget-driven: fetches visible `HomePageWidget` rows, renders each via its widget's `template_name`
- `HomepageEditorView(GMMixin, TemplateView)` — lists all widgets; shows add-widget form
- `WidgetCreateView(GMMixin, View)` — POST: create widget from type + default config; redirect to widget edit
- `WidgetUpdateView(GMMixin, UpdateView)` — edit widget config using widget's `config_form_class`
- `WidgetDeleteView(GMMixin, DeleteView)` — delete widget
- `WidgetMoveView(GMMixin, View)` — POST with `direction=up|down`; swaps `order` with adjacent widget

Add homepage URLs to `config/urls.py` at `/homepage/`.

### Step 11 — Replace `templates/home/home.html`

Widget-driven template:
```
{% for widget in widgets %}
  {% include widget.template_name with config=widget.config %}
{% empty %}
  <p>No content yet. <a href="{% url 'homepage-editor' %}">Add some widgets.</a></p>
{% endfor %}
```

The view filters `HomePageWidget` by visibility based on `request.user`:
- `public` → always shown
- `player` → shown to authenticated users
- `gm_only` → shown to GM/admin only

### Step 12 — Add widget partial templates

- `templates/home/widgets/rich_text.html`
- `templates/home/widgets/campaign_list.html`
- `templates/home/widgets/recent_entries.html`
- `templates/home/widgets/image_banner.html`
- `templates/home/homepage_editor.html` — editor UI with list, add-widget form, up/down/delete buttons

### Step 13 — Update world templates

- Delete: `world_list.html`, `world_detail.html`, `world_confirm_delete.html`
- Rename: `world_form.html` → `world_settings.html`
- Update: `campaign_*.html` — remove world slug from URLs, update breadcrumbs

### Step 14 — Update navigation partial

`templates/partials/nav.html` — replace "My Worlds" link with links to: Home, Campaigns, World Settings (GM only), Edit Homepage (GM only).

### Step 15 — Rewrite all affected tests

**Delete:**
- `tests/integration/worlds/test_membership.py`

**Rewrite:**
- `tests/unit/worlds/test_models.py` → test `WorldConfig.get_solo()`, singleton behavior, `Campaign` slug uniqueness (global, not per-world)
- `tests/unit/worlds/test_services.py` → test `get_world_config`, `update_world_config`, `create_campaign`, `get_all_campaigns`
- `tests/integration/worlds/test_worlds.py` → rename to `test_world_config.py`; test `WorldConfigUpdateView` (GM can edit, player gets 403)
- `tests/integration/worlds/test_campaigns.py` → update URLs to `/world/campaigns/...`; remove world_slug dependency

**Add:**
- `tests/unit/home/test_registry.py` → all registered widget types have required attributes; lookup by slug works
- `tests/integration/home/test_homepage_editor.py` → GM can add/delete/reorder widgets; visibility filter works for public/player/gm views

**Update `tests/conftest.py`:**
- Remove `world` fixture (no World model)
- Remove `player_member` fixture (no WorldMembership)
- Add `world_config` fixture → `WorldConfig.get_solo()`
- Add `campaign` fixture → `create_campaign(name="Test Campaign")`
- Keep `gm_user`, `player_user` (unchanged)

---

## Environment Setup

No new packages or env vars required. Verify dev environment before starting:

```bash
source .venv/bin/activate
python manage.py migrate  # ensure baseline is clean
python -m pytest          # confirm 63 tests pass before any changes
```

---

## Validation Strategy

### After each Step

Run the test suite. Expect some tests to fail during the transition — that's expected. All 63 tests should pass (or be replaced by equivalent passing tests) by Step 15.

```bash
source .venv/bin/activate && python -m pytest --tb=short -q
```

### Type and lint checks (run after Step 15)

```bash
source .venv/bin/activate
ruff check .
mypy .
```

### Migration check (after Steps 1 and 8)

```bash
python manage.py makemigrations --check  # should produce no new migrations
python manage.py migrate                  # should apply cleanly
```

### Integration test scenarios

The test suite covers these but note them for manual verification:

1. **World config is a singleton**: `WorldConfig.objects.count()` is always 1; `get_solo()` never creates a second row
2. **GM can update world settings**: POST to `/world/settings/` with valid data → 302 redirect; changes persisted
3. **Player cannot update world settings**: POST to `/world/settings/` → 403
4. **Campaign slug is globally unique**: Creating two campaigns with the same name generates `session-zero` and `session-zero-2`
5. **Homepage widget visibility**: Public widget visible to anonymous; player widget visible to logged-in player; gm_only widget hidden from player

### Manual user journeys (in browser via `docker-compose up`)

1. **GM configures world**
   - Login as GM → navigate to `/world/settings/` → change world name → save → verify nav shows new name

2. **GM creates a campaign**
   - Login as GM → `/world/campaigns/create/` → fill form → save → redirected to campaign detail

3. **GM edits the homepage**
   - Login as GM → `/homepage/edit/` → add a `rich_text` widget → save → navigate to `/` → see the widget
   - Add a `campaign_list` widget → see campaigns listed on homepage
   - Add a widget with `gm_only` visibility → logout → verify widget not shown on public homepage

4. **Player sees homepage**
   - Login as player → homepage shows player-visible and public widgets only; no gm_only widgets

5. **Anonymous user sees homepage**
   - Visit `/` without logging in → only `public` widgets shown

---

## Key Decisions to Carry Forward

- **No `WorldMembership` table**: User roles (`gm`, `player`, `admin`) on `CustomUser` are the only access control mechanism. There is no per-world or per-campaign membership.
- **`WorldConfig` is a singleton**: Never create a second row. `get_solo()` is the only constructor.
- **Widget config is JSONB**: Validated in the form, not at the DB level. Widget form classes are responsible for sanitizing config before save.
- **`CampaignForm.status` stays `required=False`**: The KB article (`campaign-form-status-field.md`) still applies — the create template hides the status field.
- **Widget ordering uses integer `order` field**: Swapping adjacent `order` values on move up/down is fine for Phase 2. A drag-and-drop reorder with a single AJAX call can replace this in a later phase.
- **`SiteConfig` is kept for CTA/meta**: `SiteConfig` in `apps/home/` retains its hero text / CTA fields. `WorldConfig` in `apps/worlds/` holds world identity (name, logo, theme). The base template can pull from both.
