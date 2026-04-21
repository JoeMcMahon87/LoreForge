# World Permission Mixins

## Decision

One mixin in `apps/worlds/mixins.py` gates access to GM-only views:

- `GMMixin` — user must be `role=gm` or `role=admin`; extends `LoginRequiredMixin`

`WorldOwnerMixin` and `WorldMemberMixin` were removed in Phase 2 when the multi-world model
was replaced with a single-world instance. There is no longer a `World` or `WorldMembership`
model — user roles on `CustomUser` are the only access control mechanism.

## Implementation pattern

The mixin manually checks `request.user.is_authenticated` first and calls
`self.handle_no_permission()` (from `AccessMixin`) to redirect unauthenticated users.
It then performs the role check before calling `super().dispatch()`.

**Do not** call `super().dispatch()` first and then check permissions — `super().dispatch()`
eventually calls the view handler (get/post), making it too late to add checks after it returns.

## Slug design

- `Campaign.slug` is globally unique (no world scoping). Collision loop:
  `Campaign.objects.filter(slug=candidate).exclude(pk=self.pk).exists()`
- Slug is only auto-generated when `self._state.adding or not self.slug` —
  never regenerated on rename, preserving stable URLs.
