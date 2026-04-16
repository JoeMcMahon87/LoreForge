---
title: Custom User Model — Set Before First Migration
category: decisions
---

## Decision

`AUTH_USER_MODEL = "accounts.CustomUser"` is defined in `config/settings/base.py`
and the initial migration was generated before any `migrate` run.

## Why

Django requires `AUTH_USER_MODEL` to be set before the first migration.
Changing it after migrations exist is a destructive operation (requires
dropping the database and starting over).

## CustomUser shape

Extends `AbstractUser`. Adds a single `role` field:
- `admin` — site-wide admin (staff-assigned only; not self-registerable)
- `gm` — Game Master, can create worlds and all entries
- `player` — read-only access to world content they're invited to

`is_gm()` and `is_admin_user()` are convenience methods for permission checks.
