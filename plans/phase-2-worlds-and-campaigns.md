# Phase 2 — Worlds & Campaigns

## Goal

GMs can create and manage worlds, invite players via a membership model (admin-only in this phase), and manage campaigns scoped to a world; all access is enforced by role-based permission mixins. A configurable public home page is served at `/`.

---

## Context

### Affected files

**New files:**
- `apps/home/__init__.py`
- `apps/home/apps.py`
- `apps/home/models.py`          — `SiteConfig` singleton
- `apps/home/views.py`
- `apps/home/admin.py`
- `apps/home/migrations/0001_initial.py` (generated)
- `templates/home/home.html`
- `apps/worlds/__init__.py`
- `apps/worlds/apps.py`
- `apps/worlds/models.py`
- `apps/worlds/services.py`
- `apps/worlds/forms.py`
- `apps/worlds/views.py`
- `apps/worlds/urls.py`
- `apps/worlds/admin.py`
- `apps/worlds/mixins.py`
- `apps/worlds/migrations/0001_initial.py` (generated)
- `templates/worlds/world_list.html`
- `templates/worlds/world_detail.html`
- `templates/worlds/world_form.html`
- `templates/worlds/world_confirm_delete.html`
- `templates/worlds/campaign_form.html`
- `templates/worlds/campaign_detail.html`
- `templates/worlds/campaign_confirm_delete.html`
- `tests/unit/home/__init__.py`
- `tests/unit/home/test_models.py`
- `tests/unit/worlds/__init__.py`
- `tests/unit/worlds/test_models.py`
- `tests/unit/worlds/test_services.py`
- `tests/integration/home/__init__.py`
- `tests/integration/home/test_home.py`
- `tests/integration/worlds/__init__.py`
- `tests/integration/worlds/test_worlds.py`
- `tests/integration/worlds/test_campaigns.py`
- `tests/integration/worlds/test_membership.py`

**Modified files:**
- `config/settings/base.py` — add `"apps.home"` and `"apps.worlds"` to `INSTALLED_APPS`
- `config/urls.py` — add home view at `/` and include `apps.worlds.urls` under `/worlds/`
- `templates/partials/nav.html` — add "My Worlds" link for authenticated users
- `tests/conftest.py` — add `world`, `campaign`, `player_member` fixtures

### External docs
- Django class-based views: https://docs.djangoproject.com/en/5.2/topics/class-based-views/
- Django `LoginRequiredMixin` / `UserPassesTestMixin`: https://docs.djangoproject.com/en/5.2/topics/auth/default/#django.contrib.auth.mixins.UserPassesTestMixin
- Django `slugify` + `unique_together`: https://docs.djangoproject.com/en/5.2/ref/models/fields/#slugfield

### Dependencies / env vars
No new packages or env vars required. All models use the Django ORM and PostgreSQL as configured in Phase 1.

---

## Database Schema

```
SiteConfig                                   # singleton — only one row ever exists
  id              BigAutoField (PK)
  site_name       CharField(max_length=100, default="LoreForge")
  hero_title      CharField(max_length=200, default="Your TTRPG world, organised.")
  hero_subtitle   CharField(max_length=400, blank=True)
  hero_body       TextField(blank=True)       # supports plain text; no HTML in v1
  cta_text        CharField(max_length=100, default="Get started")
  cta_url         CharField(max_length=200, default="/accounts/register/")
  updated_at      DateTimeField(auto_now=True)

World
  id            BigAutoField (PK)
  name          CharField(max_length=200)
  slug          SlugField(unique=True)           # auto-generated from name on save
  description   TextField(blank=True)
  owner         FK(CustomUser, related_name="owned_worlds")
  created_at    DateTimeField(auto_now_add=True)

Campaign
  id            BigAutoField (PK)
  name          CharField(max_length=200)
  slug          SlugField(max_length=200)        # auto-generated; unique within world
  world         FK(World, related_name="campaigns")
  description   TextField(blank=True)
  status        CharField choices: active | complete | hiatus  (default: active)
  created_at    DateTimeField(auto_now_add=True)
  class Meta: unique_together = [("world", "slug")]

WorldMembership
  id            BigAutoField (PK)
  user          FK(CustomUser, related_name="world_memberships")
  world         FK(World, related_name="memberships")
  role          CharField choices: gm | player
  class Meta: unique_together = [("user", "world")]
```

**Notes:**
- `World.slug` is auto-generated from `name` via `django.utils.text.slugify` in `save()`. Append a counter suffix (`-2`, `-3`, …) if slug already exists globally.
- `Campaign.slug` is auto-generated the same way but collision is checked within the same world (`Campaign.objects.filter(world=self.world, slug=candidate)`). This means two worlds can both have a campaign called "Session Zero" without conflict.
- `SiteConfig` is a singleton — enforce with a `get_solo()` classmethod: `SiteConfig.objects.get_or_create(pk=1)`. Never create a second record. The admin view should redirect to the single record rather than allowing "Add" to create a new one.
- `World.owner` always gets a corresponding `WorldMembership(role="gm")` created atomically in `services.create_world()`.
- Do not add `WorldMembership` as a through table on a M2M — use explicit FK model so the `role` field can be queried easily.

---

## Task List

### 1. `apps/home/__init__.py`
Empty file.

---

### 2. `apps/home/apps.py`
```python
from django.apps import AppConfig

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.home"
    label = "home"
```

---

### 3. `apps/home/models.py`
```python
from django.db import models
from django.utils.translation import gettext_lazy as _

class SiteConfig(models.Model):
    """Singleton site-wide configuration. Use SiteConfig.get_solo() to access."""
    site_name    = models.CharField(max_length=100, default="LoreForge")
    hero_title   = models.CharField(max_length=200, default=_("Your TTRPG world, organised."))
    hero_subtitle = models.CharField(max_length=400, blank=True)
    hero_body    = models.TextField(blank=True)
    cta_text     = models.CharField(max_length=100, default=_("Get started"))
    cta_url      = models.CharField(max_length=200, default="/accounts/register/")
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self) -> str:
        return "Site Configuration"

    @classmethod
    def get_solo(cls) -> "SiteConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

---

### 4. `apps/home/admin.py`
Singleton admin pattern — disable "Add" and redirect the changelist to the single record:
```python
from django.contrib import admin
from django.urls import reverse
from django.http import HttpResponseRedirect
from apps.home.models import SiteConfig

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteConfig.objects.exists()

    def changelist_view(self, request, extra_context=None):
        config = SiteConfig.get_solo()
        return HttpResponseRedirect(
            reverse("admin:home_siteconfig_change", args=[config.pk])
        )
```

---

### 5. `apps/home/views.py`
```python
from django.views.generic import TemplateView
from apps.home.models import SiteConfig

class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["config"] = SiteConfig.get_solo()
        return ctx
```

---

### 6. `apps/home/migrations/0001_initial.py`
Generate via `python manage.py makemigrations home`. Do not hand-write.

---

### 7. `apps/worlds/__init__.py`
Empty file.

---

### 8. `apps/worlds/apps.py`
```python
from django.apps import AppConfig

class WorldsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.worlds"
    label = "worlds"
```

---

### 9. `apps/worlds/models.py`
Define `World`, `Campaign`, `WorldMembership` per the schema above.

Key details:
- `World.save()` auto-populates `slug` via `slugify(self.name)`. If slug collides (globally), append `-2`, `-3`, etc.
- `Campaign.save()` auto-populates `slug` via `slugify(self.name)`. Collision checked within `self.world` only.
- Both `save()` methods must skip slug generation if the slug is already set and the name hasn't changed (check `self.pk` + `self._state.adding` pattern to avoid clobbering manual slugs).
- `Campaign.Status` — use `models.TextChoices`: `ACTIVE`, `COMPLETE`, `HIATUS`.
- `WorldMembership.Role` — use `models.TextChoices`: `GM`, `PLAYER`.
- Add `__str__` on all three models.
- Add `class Meta: ordering = ["-created_at"]` on `World` and `Campaign`.

---

### 10. `apps/worlds/services.py`
Business logic — keep views thin:

```python
def create_world(owner: CustomUser, name: str, description: str = "") -> World:
    """Create a world and automatically add owner as GM member (atomic)."""

def get_worlds_for_user(user: CustomUser) -> QuerySet[World]:
    """Worlds where user is owner OR has a WorldMembership. Uses .distinct()."""

def add_member(world: World, user: CustomUser, role: str) -> WorldMembership:
    """Add user to world. Raises ValueError if already a member."""

def remove_member(world: World, user: CustomUser) -> None:
    """Remove user's WorldMembership. Raises ValueError if user is the owner."""

def get_campaigns_for_world(world: World) -> QuerySet[Campaign]:
    """Return campaigns for a world ordered by created_at."""

def create_campaign(world: World, name: str, description: str = "") -> Campaign:
    """Create a campaign scoped to the given world."""
```

Use `transaction.atomic()` in `create_world` (creates World + WorldMembership together).

---

### 11. `apps/worlds/mixins.py`
Three reusable permission mixins:

```python
class GMMixin(LoginRequiredMixin):
    """Requires user to be a GM or admin."""
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_gm() or request.user.is_admin_user()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class WorldOwnerMixin(LoginRequiredMixin):
    """Requires user to be the world owner or admin.
    Views using this mixin must implement get_world()."""
    def dispatch(self, request, *args, **kwargs):
        world = self.get_world()
        if world.owner != request.user and not request.user.is_admin_user():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

class WorldMemberMixin(LoginRequiredMixin):
    """Requires user to be a member of the world (any role) or admin.
    Views using this mixin must implement get_world()."""
    def dispatch(self, request, *args, **kwargs):
        world = self.get_world()
        is_member = WorldMembership.objects.filter(world=world, user=request.user).exists()
        if not (is_member or request.user.is_admin_user()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
```

---

### 12. `apps/worlds/forms.py`
```python
class WorldForm(forms.ModelForm):
    class Meta:
        model = World
        fields = ["name", "description"]

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "description", "status"]
```
Do not include `owner`, `world`, or `slug` in forms — set in save()/service layer.

---

### 13. `apps/worlds/views.py`
All views are class-based. Keep views thin — call service functions for DB writes.

**Helper methods** — add to any view that needs objects from the URL:
```python
def get_world(self):
    return get_object_or_404(World, slug=self.kwargs["world_slug"])

def get_campaign(self):
    return get_object_or_404(Campaign, slug=self.kwargs["campaign_slug"], world=self.get_world())
```

**World views:**
| View | Mixin | URL name | Notes |
|---|---|---|---|
| `WorldListView(ListView)` | `LoginRequiredMixin` | `world-list` | Calls `get_worlds_for_user(request.user)` |
| `WorldDetailView(DetailView)` | `WorldMemberMixin` | `world-detail` | `get_world()` returns `self.object` |
| `WorldCreateView(CreateView)` | `GMMixin` | `world-create` | Calls `create_world()`; redirects to `world-detail` |
| `WorldUpdateView(UpdateView)` | `WorldOwnerMixin` | `world-update` | `slug_field="slug"`, `slug_url_kwarg="world_slug"` |
| `WorldDeleteView(DeleteView)` | `WorldOwnerMixin` | `world-delete` | Redirects to `world-list` on success |

**Campaign views:**
| View | Mixin | URL name | Notes |
|---|---|---|---|
| `CampaignCreateView(CreateView)` | `WorldOwnerMixin` | `campaign-create` | `world` set from `get_world()`; calls `create_campaign()` |
| `CampaignDetailView(DetailView)` | `WorldMemberMixin` | `campaign-detail` | Uses `get_campaign()` |
| `CampaignUpdateView(UpdateView)` | `WorldOwnerMixin` | `campaign-update` | Uses `get_campaign()` |
| `CampaignDeleteView(DeleteView)` | `WorldOwnerMixin` | `campaign-delete` | Redirects to `world-detail` on success |

---

### 14. `apps/worlds/urls.py`
```python
urlpatterns = [
    path("", views.WorldListView.as_view(), name="world-list"),
    path("create/", views.WorldCreateView.as_view(), name="world-create"),
    path("<slug:world_slug>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("<slug:world_slug>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("<slug:world_slug>/delete/", views.WorldDeleteView.as_view(), name="world-delete"),
    path("<slug:world_slug>/campaigns/create/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path("<slug:world_slug>/campaigns/<slug:campaign_slug>/", views.CampaignDetailView.as_view(), name="campaign-detail"),
    path("<slug:world_slug>/campaigns/<slug:campaign_slug>/edit/", views.CampaignUpdateView.as_view(), name="campaign-update"),
    path("<slug:world_slug>/campaigns/<slug:campaign_slug>/delete/", views.CampaignDeleteView.as_view(), name="campaign-delete"),
]
```

---

### 15. `apps/worlds/admin.py`
Register `World`, `Campaign`, `WorldMembership`.

For `WorldMembership`, use `list_display = ["user", "world", "role"]` and `list_filter = ["role", "world"]`. This is the only way to add members in Phase 2 — make it easy to use.

---

### 16. `apps/worlds/migrations/0001_initial.py`
Generate via `python manage.py makemigrations worlds`. Do not hand-write.

---

### 17. `config/settings/base.py` — add new apps
```python
"apps.home",
"apps.worlds",
```
Both must be added. `apps.home` must appear before `apps.worlds` (no dependency, but keeps ordering consistent with future apps list in the PRD).

---

### 18. `config/urls.py` — wire up home and worlds
```python
from apps.home.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("worlds/", include("apps.worlds.urls")),
]
```

Remove the old `RedirectView`. The home page is now a real view — anonymous visitors see the configured landing page; authenticated users also land here (nav bar gives them access to "My Worlds").

---

### 19. Templates

All templates extend `base.html`. Use Tailwind utility classes consistent with existing templates.

**`templates/home/home.html`**
- Renders `config.hero_title`, `config.hero_subtitle`, `config.hero_body`
- CTA button: `config.cta_text` linking to `config.cta_url`
- If user is authenticated: show a "Go to My Worlds →" link instead of (or in addition to) the CTA
- Clean hero layout, centred, large title — welcoming for first-time visitors

**`templates/worlds/world_list.html`**
- Heading: "My Worlds"
- If no worlds: empty state with a "Create your first world" CTA button (GM only — hidden for players)
- List of world cards: name (linked to `world-detail`), description excerpt, owner badge, "Edit" / "Delete" links (owner only)

**`templates/worlds/world_detail.html`** (world dashboard)
- World name, description
- Members section: list of `WorldMembership` entries (username, role badge)
- Campaigns section: list of campaigns with status badge; "Add Campaign" button (owner only)
- "Edit World" / "Delete World" links (owner only)

**`templates/worlds/world_form.html`**
- Used for both create and edit (`{% if form.instance.pk %}Edit{% else %}Create{% endif %}`)
- All inputs have `<label>` elements; errors linked via `aria-describedby`

**`templates/worlds/world_confirm_delete.html`**
- Shows world name; "Delete" and "Cancel" buttons

**`templates/worlds/campaign_form.html`**
- Create / edit form for Campaign; shows parent world name as page context
- Status field shown on edit only (new campaigns default to `active`)

**`templates/worlds/campaign_detail.html`**
- Campaign name, status badge (colour-coded: green=active, grey=complete, yellow=hiatus), description, parent world breadcrumb
- Placeholder sections for entries and timeline ("Coming in a future update")

**`templates/worlds/campaign_confirm_delete.html`**
- Shows campaign name and parent world; "Delete" and "Cancel" buttons

---

### 20. `templates/partials/nav.html` — add "My Worlds" link
For authenticated users, insert before the logout button:
```html
<li>
  <a href="{% url 'world-list' %}"
     class="px-3 py-1.5 rounded hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-white">
    {% trans "My Worlds" %}
  </a>
</li>
```

---

### 21. `tests/conftest.py` — add fixtures
```python
@pytest.fixture
def world(db, gm_user):
    from apps.worlds.services import create_world
    return create_world(owner=gm_user, name="Test World")

@pytest.fixture
def campaign(db, world):
    from apps.worlds.services import create_campaign
    return create_campaign(world=world, name="Test Campaign")

@pytest.fixture
def player_member(db, world, player_user):
    from apps.worlds.services import add_member
    return add_member(world=world, user=player_user, role="player")
```

---

### 22. `tests/unit/home/test_models.py`
- `SiteConfig.get_solo()` creates a record with defaults on first call
- `SiteConfig.get_solo()` returns the same record on subsequent calls (no duplicate)
- `SiteConfig.__str__()` returns `"Site Configuration"`

### 23. `tests/unit/worlds/test_models.py`
- `World.__str__()` returns name
- `World.save()` auto-generates slug from name
- World slug collision produces `-2` suffix
- `Campaign.__str__()` returns name
- `Campaign.save()` auto-generates slug from name
- Campaign slug collision is checked within the same world (two worlds can share a slug)
- `Campaign` default status is `active`
- `WorldMembership` unique_together prevents duplicate `(user, world)` pairs

### 24. `tests/unit/worlds/test_services.py`
- `create_world()` creates World + WorldMembership(role=gm) atomically
- `get_worlds_for_user()` returns worlds where user is owner
- `get_worlds_for_user()` returns worlds where user is a non-owner member
- `get_worlds_for_user()` excludes worlds the user has no membership in
- `get_worlds_for_user()` returns no duplicates when user is both owner and member
- `add_member()` creates a WorldMembership
- `add_member()` raises `ValueError` if user is already a member
- `remove_member()` removes membership
- `remove_member()` raises `ValueError` if user is the world owner
- `create_campaign()` associates campaign with correct world

### 25. `tests/integration/home/test_home.py`
- `GET /` returns 200 for anonymous users
- `GET /` returns 200 for authenticated users
- Home page renders `config.hero_title` from `SiteConfig`
- Updating `SiteConfig` via `get_solo()` and saving causes new content to appear on `GET /`

### 26. `tests/integration/worlds/test_worlds.py`
- `GET /worlds/` requires login (anonymous → 302 to login)
- `GET /worlds/` for GM shows their worlds
- `GET /worlds/` for player shows worlds they are members of
- `POST /worlds/create/` as GM creates world, redirects to `world-detail`
- `POST /worlds/create/` as player returns 403
- `GET /worlds/<slug>/` as world member returns 200
- `GET /worlds/<slug>/` as non-member returns 403
- `GET /worlds/<slug>/` as anonymous returns 302 to login
- `POST /worlds/<slug>/edit/` as owner updates world
- `POST /worlds/<slug>/edit/` as player returns 403
- `POST /worlds/<slug>/delete/` as owner deletes world, redirects to `world-list`
- `POST /worlds/<slug>/delete/` as non-owner returns 403

### 27. `tests/integration/worlds/test_campaigns.py`
- `POST /worlds/<slug>/campaigns/create/` as owner creates campaign
- `POST /worlds/<slug>/campaigns/create/` as player returns 403
- `GET /worlds/<slug>/campaigns/<campaign_slug>/` as member returns 200
- `GET /worlds/<slug>/campaigns/<campaign_slug>/` as non-member returns 403
- `POST /worlds/<slug>/campaigns/<campaign_slug>/edit/` as owner updates campaign
- `POST /worlds/<slug>/campaigns/<campaign_slug>/delete/` as owner deletes, redirects to `world-detail`

### 28. `tests/integration/worlds/test_membership.py`
- Owner is automatically a GM member after `create_world()`
- Player added via `add_member()` can access `world-detail` (200)
- Non-member gets 403 on `world-detail`

---

## Environment Setup

No new packages or env vars required beyond Phase 1.

Before coding begins:
1. Activate venv: `source .venv/bin/activate`
2. Confirm `.env` exists (created in Phase 1 validation)
3. `pytest` runs against SQLite in-memory — no running Postgres needed for tests

---

## Validation Strategy

Run each step in order. Do not proceed if a step fails.

### Step 1 — Lint and type-check
```bash
ruff check . && mypy .
```
Expected: zero errors.

### Step 2 — Migrations clean
```bash
python manage.py makemigrations --check
```
Expected: "No changes detected" — `0001_initial.py` for both `home` and `worlds` are committed.

### Step 3 — Unit tests
```bash
pytest tests/unit/ -v
```
Expected: all 5 existing + new unit tests pass (~18 total).

Covered:
- `SiteConfig` singleton behaviour
- `World` and `Campaign` slug auto-generation and collision avoidance
- All service function happy paths and error paths

### Step 4 — Integration tests
```bash
pytest tests/integration/ -v
```
Expected: all 7 existing + new integration tests pass (~31 total).

Covered:
- Home page accessible anonymously and when authenticated
- Anonymous redirect to login on protected world URLs
- 403 enforcement for players attempting GM actions
- Full CRUD for worlds and campaigns as owner
- Member (non-owner) read-only access

### Step 5 — Full suite with coverage
```bash
pytest --cov=apps --cov-report=term-missing
```
Expected: all tests pass; `apps/home/` and `apps/worlds/` coverage ≥ 90%.

### Step 6 — Manual user journey (browser)
Requires `python manage.py runserver` with a running Postgres instance.

**Home page:**
1. Navigate to `http://localhost:8000/` as anonymous → home page loads with hero text
2. Open Django admin → Site Configuration → edit hero title → save
3. Reload `/` → updated title visible

**GM flow:**
1. Register as GM → lands on home page with "My Worlds" in nav
2. Click "My Worlds" → `/worlds/` with empty state and "Create your first world" CTA
3. Create a world → redirected to world dashboard
4. Add a campaign → campaign appears in dashboard with "active" badge
5. Click campaign → campaign detail loads at `/worlds/<world-slug>/campaigns/<campaign-slug>/`
6. Edit campaign → change status to "complete" → badge updates
7. Delete campaign → back to world dashboard
8. Edit world → name changes; slug remains unchanged (verify in URL)
9. Delete world → back to world list (empty)

**Player flow:**
1. Register as player → home page, "My Worlds" in nav
2. `/worlds/` → empty list, no "Create" button visible
3. Attempt `/worlds/<any-slug>/` → 403
4. Log in as GM → Django admin → WorldMembership → Add membership for player
5. Log in as player → `/worlds/` shows the world
6. Click world → dashboard visible; no "Edit World" / "Delete World" / "Add Campaign" controls
7. Click a campaign → campaign detail visible

### Step 7 — Accessibility spot-check
- `/` home page has a descriptive `<h1>` (not just the site name)
- All world/campaign forms have associated `<label>` elements
- Delete confirmations show the entity name so users know what they're deleting
- "My Worlds" nav link is keyboard-reachable and has visible focus ring
- Status badges use both colour and text (not colour alone)

---

## Notes for the Implementation Session

- **Slug uniqueness — World**: unique globally. Slug collision loop queries `World.objects.filter(slug=candidate).exists()`.
- **Slug uniqueness — Campaign**: unique per world. Collision loop queries `Campaign.objects.filter(world=self.world, slug=candidate).exists()`. Two worlds can both have `session-zero`.
- **`Campaign.save()` slug guard**: only auto-generate slug when `self._state.adding` is True (new record) or when slug is empty. Don't regenerate on every save — that would break URLs when someone renames a campaign.
- **`SiteConfig` admin singleton**: the `changelist_view` redirect ensures editors land directly on the edit page, never a list. `has_add_permission` returns `False` once one record exists. This is a widely-used Django pattern, no third-party package needed.
- **Home page for authenticated users**: do not redirect away from `/` — show the same page with an extra "Go to My Worlds" link. The home page is public and should be welcoming to both new visitors and returning users.
- **`WorldUpdateView` slug**: set `slug_field = "slug"` and `slug_url_kwarg = "world_slug"` on the view. Django's `UpdateView` uses these to look up the object.
- **Campaign `CampaignUpdateView`/`CampaignDetailView`**: these can't use Django's built-in slug lookup because the slug is only unique within a world. Use `get_campaign()` helper (manually fetches by `world` + `slug`) rather than relying on `get_object()`.
- **Invite UI is admin-only in this phase**: `add_member()` is exercised via fixtures in tests and via the Django admin in manual testing. A UI for inviting players by username/email is deferred to a later phase.
- **Player "My Worlds" list**: `get_worlds_for_user()` must handle the case where the user is both owner and a WorldMembership record (which is always true after `create_world()`). Use `.distinct()` on a `Q(owner=user) | Q(memberships__user=user)` filter to avoid duplicates.
- **Future phases**: Phase 3 (Worldbook Entries) adds an `Entry` abstract model with a `world` FK and a `campaign` optional FK. The `World` and `Campaign` models are load-bearing anchors — keep them stable and avoid adding phase-3 fields in advance.
- **`LOGIN_REDIRECT_URL`**: currently set to `"/"` in base settings, which now resolves to the real home view. No change needed — this is already correct.
