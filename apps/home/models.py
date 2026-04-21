from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfig(models.Model):
    """Singleton site-wide configuration. Use SiteConfig.get_solo() to access."""

    site_name = models.CharField(max_length=100, default="LoreForge")
    hero_title = models.CharField(
        max_length=200, default=_("Your TTRPG world, organised.")
    )
    hero_subtitle = models.CharField(max_length=400, blank=True)
    hero_body = models.TextField(blank=True)
    cta_text = models.CharField(max_length=100, default=_("Get started"))
    cta_url = models.CharField(max_length=200, default="/accounts/register/")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self) -> str:
        return "Site Configuration"

    @classmethod
    def get_solo(cls) -> "SiteConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomePageWidget(models.Model):
    class Visibility(models.TextChoices):
        GM_ONLY = "gm_only", _("GM only")
        PLAYER = "player", _("Player")
        PUBLIC = "public", _("Public")

    widget_type = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict)
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.PUBLIC
    )

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.widget_type} (order={self.order})"
