# World Permission Mixins

## Decision

Three mixins in `apps/worlds/mixins.py` gate access to world views:

- `GMMixin` — user must be `role=gm` or `role=admin`
- `WorldOwnerMixin` — user must be `world.owner` or admin; view must implement `get_world()`
- `WorldMemberMixin` — user must have a `WorldMembership` for the world, or be admin; view must implement `get_world()`

All three extend `LoginRequiredMixin`.

## Implementation pattern

The mixins manually check `request.user.is_authenticated` first and call `self.handle_no_permission()` (from `AccessMixin`) to redirect unauthenticated users. They then perform the world/role check before calling `super().dispatch()`.

**Do not** call `super().dispatch()` first and then check permissions — `super().dispatch()` eventually calls the view handler (get/post), making it too late to add checks after it returns.

## Slug design

- `World.slug` is unique globally. Collision loop: `World.objects.filter(slug=candidate).exists()`
- `Campaign.slug` is unique per world. Two worlds can share the same campaign slug.
- Both models only auto-generate slug when `self._state.adding or not self.slug` — slug is never regenerated on rename, preserving stable URLs.
