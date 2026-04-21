from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class GMMixin(LoginRequiredMixin):
    """Requires user to be a GM or admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_gm() or request.user.is_admin_user()):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
