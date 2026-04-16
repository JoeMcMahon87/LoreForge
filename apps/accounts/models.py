from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        GM = "gm", _("Game Master")
        PLAYER = "player", _("Player")

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PLAYER,
    )

    def is_gm(self) -> bool:
        return self.role == self.Role.GM

    def is_admin_user(self) -> bool:
        return self.role == self.Role.ADMIN
