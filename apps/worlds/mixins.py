from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from apps.worlds.models import WorldMembership


class GMMixin(LoginRequiredMixin):
    """Requires user to be a GM or admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_gm() or request.user.is_admin_user()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class WorldOwnerMixin(LoginRequiredMixin):
    """Requires user to be the world owner or admin.
    Views using this mixin must implement get_world()."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        world = self.get_world()  # type: ignore[attr-defined]
        if world.owner != request.user and not request.user.is_admin_user():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class WorldMemberMixin(LoginRequiredMixin):
    """Requires user to be a member of the world (any role) or admin.
    Views using this mixin must implement get_world()."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        world = self.get_world()  # type: ignore[attr-defined]
        is_member = WorldMembership.objects.filter(
            world=world, user=request.user
        ).exists()
        if not (is_member or request.user.is_admin_user()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
