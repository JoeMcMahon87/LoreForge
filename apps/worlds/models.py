from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class World(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_worlds",
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
            while World.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Campaign(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        COMPLETE = "complete", _("Complete")
        HIATUS = "hiatus", _("Hiatus")

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    world = models.ForeignKey(World, on_delete=models.CASCADE, related_name="campaigns")
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("world", "slug")]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding or not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Campaign.objects.filter(world=self.world, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class WorldMembership(models.Model):
    class Role(models.TextChoices):
        GM = "gm", _("Game Master")
        PLAYER = "player", _("Player")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="world_memberships",
    )
    world = models.ForeignKey(
        World, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=Role.choices)

    class Meta:
        unique_together = [("user", "world")]

    def __str__(self) -> str:
        return f"{self.user} — {self.world} ({self.role})"
