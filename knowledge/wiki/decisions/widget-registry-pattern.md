# Widget Registry Pattern

## Decision

The homepage widget system uses a module-level dict in `apps/home/registry.py` as a simple
registry mapping `type_slug → widget class`. Widgets are registered at import time.

## Structure

Each widget type is a class inheriting `BaseWidget` (`apps/home/widgets.py`) with:

- `type_slug: str` — stored in `HomePageWidget.widget_type`
- `label: str` — shown in the editor widget picker
- `template_name: str` — partial template path
- `config_form_class: type[forms.Form] | None` — form for editing config (or `None`)
- `get_context(config: dict) -> dict` — returns template context from stored JSONB config

Core widgets: `rich_text`, `campaign_list`, `recent_entries`, `image_banner`.

## How to add a new widget type

1. Subclass `BaseWidget` in `apps/home/widgets.py`
2. Call `_register(MyWidget)` in `apps/home/registry.py`
3. Add a partial template at the path declared in `template_name`
4. Add it to `templates/home/home.html`'s `{% if widget_type == ... %}` dispatch block

Phase 8 (module system) will extend the registry from installed modules' `ModuleManifest`.

## Widget config

Config is stored as JSONB in `HomePageWidget.config`. The `config_form_class` validates and
sanitizes before save. Never rely on DB-level validation of config shape.
