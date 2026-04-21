from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class WorldConfig(models.Model):
    name = models.CharField(max_length=200, default="My World")
    tagline = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    theme_color = models.CharField(max_length=7, default="#4f46e5")
    logo = models.ImageField(upload_to="world/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "World Configuration"

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_solo(cls) -> "WorldConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETE = "complete", _("Complete")
        HIATUS = "hiatus", _("Hiatus")

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding or not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Campaign.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
