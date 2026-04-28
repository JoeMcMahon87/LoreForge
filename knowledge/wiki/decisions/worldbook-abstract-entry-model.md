# Worldbook: Abstract Entry Model

## Decision
`Entry` is an abstract Django model (`Meta: abstract = True`). Each concrete type (Location, Faction, Item, Lore) gets its own DB table with all Entry fields duplicated.

## Consequences
- `Tag` M2M creates 4 separate through tables (one per concrete type). Phase 7 search will union QuerySets across models.
- Slug uniqueness is per-type: `/worldbook/locations/dragon-peak/` and `/worldbook/factions/dragon-peak/` can coexist.
- `save()` on abstract `Entry` uses `self.__class__.objects` to target the concrete model's table for collision-suffix slug generation.
- `created_by` FK uses `null=True, blank=True, on_delete=SET_NULL` so user deletion does not cascade-delete entries.

## Visibility Filtering
`get_visible_queryset(model_class, user)` in `services.py` returns:
- GM/admin: all entries
- Authenticated player: `visibility__in=["player", "public"]`
- Anonymous: `visibility="public"`

List/detail views have no auth gate — non-visible entries return 404 via `get_object_or_404` on the filtered QS. Only create/update/delete views require `GMMixin`.
