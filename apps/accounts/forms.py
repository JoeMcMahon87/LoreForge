from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import CustomUser


class RegistrationForm(UserCreationForm):
    """Registration form — admin role is not self-assignable."""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict role choices to gm and player — admin is staff-assigned only
        self.fields["role"].choices = [
            (CustomUser.Role.GM, _("Game Master")),
            (CustomUser.Role.PLAYER, _("Player")),
        ]
        self.fields["email"].required = True
