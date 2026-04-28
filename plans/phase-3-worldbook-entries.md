# Phase 3 — Worldbook Entries

## Goal
GM can create, edit, and delete Location, Faction, Item, and Lore entries with per-entry visibility controls; players and anonymous visitors see only entries they are permitted to view.

---

## Context

### Affected files

**New — app scaffold:**
- `apps/worldbook/__init__.py`
- `apps/worldbook/apps.py`
- `apps/worldbook/admin.py`
- `apps/worldbook/models.py`
- `apps/worldbook/services.py`
- `apps/worldbook/forms.py`
- `apps/worldbook/views.py`
- `apps/worldbook/urls.py`
- `apps/worldbook/migrations/__init__.py`
- `apps/worldbook/migrations/0001_initial.py` (generated)

**New — templates (18 total):**
- `templates/worldbook/_entry_form_base.html` — shared form fields partial (title, content, visibility, tags)
- `templates/worldbook/_entry_card.html` — list item partial
- `templates/worldbook/location_list.html`
- `templates/worldbook/location_detail.html`
- `templates/worldbook/location_form.html` (extends `_entry_form_base.html`)
- `templates/worldbook/location_confirm_delete.html`
- `templates/worldbook/faction_list.html`
- `templates/worldbook/faction_detail.html`
- `templates/worldbook/faction_form.html`
- `templates/worldbook/faction_confirm_delete.html`
- `templates/worldbook/item_list.html`
- `templates/worldbook/item_detail.html`
- `templates/worldbook/item_form.html`
- `templates/worldbook/item_confirm_delete.html`
- `templates/worldbook/lore_list.html`
- `templates/worldbook/lore_detail.html`
- `templates/worldbook/lore_form.html`
- `templates/worldbook/lore_confirm_delete.html`

**New — tests:**
- `tests/unit/worldbook/__init__.py`
- `tests/unit/worldbook/test_models.py`
- `tests/integration/worldbook/__init__.py`
- `tests/integration/worldbook/test_locations.py`
- `tests/integration/worldbook/test_factions.py`
- `tests/integration/worldbook/test_items.py`
- `tests/integration/worldbook/test_lore.py`

**Modified:**
- `config/settings/base.py` — add `"apps.worldbook"` to `INSTALLED_APPS`
- `config/urls.py` — add `path("worldbook/", include("apps.worldbook.urls"))`
- `templates/partials/nav.html` — add Worldbook nav link
- `tests/conftest.py` — add entry fixtures (location, faction, item, lore)

### External docs to reference
- Django abstract model docs: https://docs.djangoproject.com/en/5.2/topics/db/models/#abstract-base-classes
- Django M2M on abstract models: each concrete model gets its own through table (expected behavior)
- No new packages needed

### Dependencies or env vars needed
None. Pillow is already installed (used by WorldConfig.logo). No new pip installs.

---

## Key Design Decisions

### 1. Abstract base, not multi-table inheritance
Use `abstract = True` on `Entry` — this matches the PRD's language ("abstract base — concrete tables per type") and gives per-type slug uniqueness. Each concrete model (Location, Faction, Item, Lore) gets its own DB table with all Entry fields duplicated.

Trade-off: `Tag` M2M creates 4 separate through tables (one per concrete type). Phase 7 search will union QuerySets across models. This is acceptable for v1 and avoids the pointer-table overhead of multi-table inheritance.

### 2. Slug uniqueness is per-type
Because each concrete model has its own table and `slug = SlugField(unique=True)`, slug uniqueness is per entry type. `/worldbook/locations/dragon-peak/` and `/worldbook/factions/dragon-peak/` are both valid. The auto-suffix logic (same as Campaign) prevents collisions within a type.

### 3. No LoginRequired on list/detail views
Entries have a `visibility` field. Anonymous users may see `public` entries without logging in. All list/detail views call `get_visible_queryset(model_class, user)` from services, which returns the correctly-filtered QS. If an entry is not in the allowed QS, `get_object_or_404` raises 404 (not a login redirect). Only create/edit/delete views use `GMMixin`.

### 4. `created_by` is nullable FK with SET_NULL
A user deletion should not cascade-delete world entries. `created_by = ForeignKey(..., null=True, blank=True, on_delete=SET_NULL)`.

### 5. Template strategy: shared base form, per-type list/detail
`_entry_form_base.html` contains the common fields block (title, content, visibility, tags). Each type-specific form template extends `base.html`, includes the base form partial, and adds its own extra fields section. This avoids repeating the common fields across 4 forms.

---

## Task List

### Step 1 — App scaffold
Create `apps/worldbook/` directory with empty `__init__.py`, `admin.py`, `apps.py` (label `"worldbook"`), and `migrations/__init__.py`.

### Step 2 — Models (`apps/worldbook/models.py`)

```
Tag
  name CharField(100, unique=True)
  slug SlugField(100, unique=True)   ← auto-generated from name in save()
  __str__ → name

Entry [abstract]
  Visibility = TextChoices: GM_ONLY="gm_only", PLAYER="player", PUBLIC="public"
  title CharField(200)
  slug SlugField(200, unique=True)   ← auto-generated, stable on rename
  content TextField(blank=True)
  visibility CharField(10, choices, default=GM_ONLY)
  created_by FK(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL)
  tags M2M(Tag, blank=True)
  created_at DateTimeField(auto_now_add=True)
  updated_at DateTimeField(auto_now=True)
  Meta: abstract=True, ordering=["-updated_at"]
  save(): auto-slug with collision-suffix logic (same pattern as Campaign.save)
  __str__ → title

Location(Entry)
  lat FloatField(null=True, blank=True)
  lng FloatField(null=True, blank=True)
  region CharField(200, blank=True)
  location_type CharField(100, blank=True)
  parent_location FK("self", null=True, blank=True, on_delete=SET_NULL, related_name="children")
  Meta: verbose_name="Location"

Faction(Entry)
  alignment CharField(100, blank=True)
  goals TextField(blank=True)
  Meta: verbose_name="Faction"

Item(Entry)
  Rarity = TextChoices: COMMON, UNCOMMON, RARE, VERY_RARE, LEGENDARY, ARTIFACT
  item_type CharField(100, blank=True)
  rarity CharField(20, choices, default=COMMON)
  Meta: verbose_name="Item"

Lore(Entry)
  LoreType = TextChoices: HISTORY, MYTH, LEGEND, OTHER
  lore_type CharField(20, choices, default=OTHER)
  Meta: verbose_name="Lore"
```

### Step 3 — Migrations
```
python manage.py makemigrations worldbook
```

### Step 4 — Services (`apps/worldbook/services.py`)

```python
def get_visible_queryset(model_class, user):
    """Filter entries by the requesting user's role."""
    # GM / admin sees all; player sees player+public; anonymous sees public only
    ...

# One create function per type (thin wrappers that call model.objects.create)
def create_location(title, content, visibility, created_by, **kwargs) -> Location
def create_faction(title, content, visibility, created_by, **kwargs) -> Faction
def create_item(title, content, visibility, created_by, **kwargs) -> Item
def create_lore(title, content, visibility, created_by, **kwargs) -> Lore
```

Service functions must not call `request`; they accept plain Python values so they are testable without HTTP.

### Step 5 — Forms (`apps/worldbook/forms.py`)

One ModelForm per concrete type. All forms include `title, content, visibility, tags` plus type-specific fields. `tags` uses Django's default M2M widget for v1 (multi-select; JS enhancement deferred).

### Step 6 — Views (`apps/worldbook/views.py`)

Four groups of 5 views each (20 views total). Pattern per type:

```
<Type>ListView       — no auth gate; get_queryset calls get_visible_queryset
<Type>DetailView     — no auth gate; get_object calls get_object_or_404 on visible QS
<Type>CreateView     — GMMixin; form_valid calls create_<type>() service
<Type>UpdateView     — GMMixin; get_object by slug
<Type>DeleteView     — GMMixin; get_object by slug; success_url → type list
```

Context naming: `context_object_name = "entry"` on detail views (generic — templates can also access the typed object).

### Step 7 — URLs (`apps/worldbook/urls.py`)

```
/worldbook/locations/                          name="location-list"
/worldbook/locations/create/                   name="location-create"
/worldbook/locations/<slug:entry_slug>/        name="location-detail"
/worldbook/locations/<slug:entry_slug>/edit/   name="location-update"
/worldbook/locations/<slug:entry_slug>/delete/ name="location-delete"
(same pattern for factions/, items/, lore/)
```

URL kwarg: `entry_slug` (consistent across all types; avoids shadowing Django's built-in `slug`).

### Step 8 — Wire up

**`config/settings/base.py`**: uncomment `"apps.worldbook"` in `INSTALLED_APPS`.

**`config/urls.py`**: add `path("worldbook/", include("apps.worldbook.urls"))`.

### Step 9 — Templates

**`templates/worldbook/_entry_form_base.html`** (include-able partial):
- Fields: title (required), content (textarea), visibility (select), tags (multi-select)
- WCAG: label+input pairings, aria-describedby on errors, `role="alert"` on error paragraphs

**`templates/worldbook/_entry_card.html`** (include-able partial):
- Shows: title (linked to detail), visibility badge (color-coded), tags, updated_at

**Per-type list template** (`location_list.html` etc.):
- Heading + "Create" button (GM-only: wrap in `{% if request.user.is_gm or request.user.is_admin_user %}`)
- Empty state message
- Loop: `{% include "worldbook/_entry_card.html" with entry=location %}`

**Per-type detail template** (`location_detail.html` etc.):
- Breadcrumb → type list → entry title
- Full content render
- Type-specific fields section
- Edit/Delete buttons (GM-only)
- Tags display

**Per-type form template** (`location_form.html` etc.):
- Extends `base.html`
- Includes `_entry_form_base.html`
- Type-specific fields block after common fields

**Per-type confirm-delete template** (`location_confirm_delete.html` etc.):
- Same pattern as `campaign_confirm_delete.html`

### Step 10 — Admin (`apps/worldbook/admin.py`)
Register Tag, Location, Faction, Item, Lore with `@admin.register`.

### Step 11 — Nav update
Add a "Worldbook" dropdown to `templates/partials/nav.html` using Tailwind's `group`/`group-hover` utilities — no JS required. The dropdown reveals links to all four entry-type lists.

```html
<!-- Worldbook dropdown — CSS-only via Tailwind group -->
<li class="relative group">
  <button class="px-3 py-1.5 rounded hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-white"
          aria-haspopup="true" aria-expanded="false">
    Worldbook ▾
  </button>
  <ul class="absolute left-0 top-full hidden group-hover:block group-focus-within:block
             bg-indigo-800 rounded shadow-lg py-1 min-w-max z-50"
      role="menu">
    <li role="none"><a href="{% url 'location-list' %}" role="menuitem" class="block px-4 py-2 hover:bg-indigo-700">Locations</a></li>
    <li role="none"><a href="{% url 'faction-list' %}" role="menuitem" class="block px-4 py-2 hover:bg-indigo-700">Factions</a></li>
    <li role="none"><a href="{% url 'item-list' %}"    role="menuitem" class="block px-4 py-2 hover:bg-indigo-700">Items</a></li>
    <li role="none"><a href="{% url 'lore-list' %}"    role="menuitem" class="block px-4 py-2 hover:bg-indigo-700">Lore</a></li>
  </ul>
</li>
```

WCAG notes: `aria-haspopup`, `aria-expanded`, `role="menu"` / `role="menuitem"` on the list; `group-focus-within` keeps the menu open when keyboard focus moves into the submenu links.

### Step 12 — Fixtures in `tests/conftest.py`
Add:
```python
@pytest.fixture
def gm_user_with_location(db, gm_user):
    from apps.worldbook.services import create_location
    loc = create_location(title="Dragon Peak", content="...", visibility="gm_only", created_by=gm_user)
    return gm_user, loc
```
Or simpler individual fixtures:
```python
@pytest.fixture
def location(db, gm_user): ...
@pytest.fixture
def faction(db, gm_user): ...
@pytest.fixture
def item(db, gm_user): ...
@pytest.fixture
def lore(db, gm_user): ...
```

### Step 13 — Unit tests (`tests/unit/worldbook/test_models.py`)

Cover:
- `Tag`: str, slug auto-generated from name
- `Location`: slug auto-generated from title, stable on rename, collision gets suffix
- `Location`: default visibility is `gm_only`
- `Faction`, `Item`, `Lore`: str returns title, type-specific field defaults
- `Item`: rarity defaults to COMMON
- `Lore`: lore_type defaults to OTHER

### Step 14 — Integration tests (`tests/integration/worldbook/`)

**`test_locations.py`** (canonical full test — covers the visibility + CRUD contract):
```
TestLocationListView
  test_anonymous_sees_only_public_entries
  test_player_sees_public_and_player_entries
  test_gm_sees_all_entries
  test_empty_state_renders

TestLocationDetailView
  test_gm_can_view_gm_only_entry
  test_player_cannot_access_gm_only_entry_gets_404
  test_anonymous_cannot_access_player_entry_gets_404
  test_anonymous_can_view_public_entry

TestLocationCreateView
  test_gm_can_create_location
  test_player_gets_403
  test_anonymous_redirects_to_login

TestLocationUpdateView
  test_gm_can_update_location
  test_player_gets_403

TestLocationDeleteView
  test_gm_can_delete_location
  test_player_gets_403
```

**`test_factions.py`**, **`test_items.py`**, **`test_lore.py`**:
Lighter — cover CRUD (create, update, delete) and one visibility check each. Full visibility logic is already tested in location tests.

---

## Environment Setup

No new environment variables or pip packages required.

Before coding:
```bash
source .venv/bin/activate
```

After writing models (Step 2):
```bash
python manage.py makemigrations worldbook
python manage.py migrate
```

---

## Validation Strategy

### Type checks + lint
```bash
source .venv/bin/activate
ruff check . && mypy .
```
Expected: zero errors. If mypy complains about abstract model, check that `Entry` has `class Meta: abstract = True` and that all FKs use `settings.AUTH_USER_MODEL`.

### Unit tests
```bash
pytest tests/unit/worldbook/ -v
```

### Integration tests
```bash
pytest tests/integration/worldbook/ -v
```

### Full suite
```bash
pytest
```
All 57 existing tests must still pass plus the new worldbook tests.

### Manual user journeys (in browser at `http://localhost:8000`)

**GM flow:**
1. Log in as a GM user.
2. Navigate to `/worldbook/locations/` — see empty state with "Create Location" button.
3. Click "Create Location" → fill in title "Dragon Peak", content, visibility = GM Only → save.
4. Verify redirect to detail page showing "Dragon Peak".
5. Click "Edit" → change visibility to Player → save.
6. Log out, log in as a player user.
7. Navigate to `/worldbook/locations/` — "Dragon Peak" should appear (Player visibility).
8. Navigate to `/worldbook/locations/dragon-peak/edit/` — should get 403.
9. Log out (anonymous).
10. Navigate to `/worldbook/locations/` — "Dragon Peak" should NOT appear (not Public).
11. Navigate to `/worldbook/locations/dragon-peak/` — should get 404.

**GM — change to public:**
12. Log in as GM, change "Dragon Peak" to Public.
13. Log out, navigate to `/worldbook/locations/dragon-peak/` — entry should load without login.

**Slug collision:**
14. As GM, create two entries both named "Dragon Peak" (one after the other).
15. Second should auto-slug to `dragon-peak-2`.

**All four types:**
16. Repeat creation for Faction, Item, and Lore to confirm all routes work.
