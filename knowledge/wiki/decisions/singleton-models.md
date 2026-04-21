# Singleton Model Pattern

## Decision

Both `SiteConfig` (in `apps/home/`) and `WorldConfig` (in `apps/worlds/`) use the same
singleton pattern: a `get_solo()` classmethod that calls `get_or_create(pk=1)`.

```python
@classmethod
def get_solo(cls) -> "MyModel":
    obj, _ = cls.objects.get_or_create(pk=1)
    return obj
```

## Why

Single-world instance model means there is always exactly one `WorldConfig` row and one
`SiteConfig` row. `get_or_create(pk=1)` is the safe constructor — never create rows directly.

## Two singletons, different purposes

- `SiteConfig` — site-level CTA/hero text for the landing page (owned by `apps/home/`)
- `WorldConfig` — world identity: name, tagline, logo, theme color (owned by `apps/worlds/`)

The base template and home view can pull from both simultaneously.

## Update pattern

`WorldConfigUpdateView` overrides `get_object()` to return `WorldConfig.get_solo()` rather
than looking up by URL pk — the URL has no pk segment for singleton edit pages.
