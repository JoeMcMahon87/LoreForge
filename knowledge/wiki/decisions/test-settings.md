---
title: Test Settings — SQLite vs PostgreSQL
category: decisions
---

## Decision

`config/settings/test.py` uses SQLite (`:memory:`) as the test database.
`pyproject.toml` sets `DJANGO_SETTINGS_MODULE = "config.settings.test"`.

## Why

The dev/CI environment may not always have a live PostgreSQL instance.
SQLite in-memory is sufficient for unit and integration tests that cover
model behaviour, auth flows, and view responses.

## Trade-offs

- SQLite does not support all PostgreSQL features (e.g. `SearchVector`, `JSONB`).
  Tests that rely on PostgreSQL-specific functionality must be skipped or
  run with `DJANGO_SETTINGS_MODULE=config.settings.dev` against a real DB.
- The `--reuse-db` flag in pyproject.toml is a no-op with `:memory:` (always fresh).

## Future

Phase 7 (Full-Text Search) and Phase 8 (Plugin Module System / JSONB) will need
PostgreSQL-backed tests. Add a `pytest.ini_options` marker (e.g. `postgres_only`)
and a CI step that runs those tests against a real DB.
