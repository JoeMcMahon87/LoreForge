from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding or not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 2
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Entry(models.Model):
    class Visibility(models.TextChoices):
        GM_ONLY = "gm_only", _("GM Only")
        PLAYER = "player", _("Player")
        PUBLIC = "public", _("Public")

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True)
    visibility = models.CharField(
        max_length=10, choices=Visibility.choices, default=Visibility.GM_ONLY
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if self._state.adding or not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2
            while self.__class__.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Location(Entry):
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    region = models.CharField(max_length=200, blank=True)
    location_type = models.CharField(max_length=100, blank=True)
    parent_location = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    class Meta(Entry.Meta):
        verbose_name = "Location"


class Faction(Entry):
    alignment = models.CharField(max_length=100, blank=True)
    goals = models.TextField(blank=True)

    class Meta(Entry.Meta):
        verbose_name = "Faction"


class Item(Entry):
    class Rarity(models.TextChoices):
        COMMON = "common", _("Common")
        UNCOMMON = "uncommon", _("Uncommon")
        RARE = "rare", _("Rare")
        VERY_RARE = "very_rare", _("Very Rare")
        LEGENDARY = "legendary", _("Legendary")
        ARTIFACT = "artifact", _("Artifact")

    item_type = models.CharField(max_length=100, blank=True)
    rarity = models.CharField(
        max_length=20, choices=Rarity.choices, default=Rarity.COMMON
    )

    class Meta(Entry.Meta):
        verbose_name = "Item"


class Lore(Entry):
    class LoreType(models.TextChoices):
        HISTORY = "history", _("History")
        MYTH = "myth", _("Myth")
        LEGEND = "legend", _("Legend")
        OTHER = "other", _("Other")

    lore_type = models.CharField(
        max_length=20, choices=LoreType.choices, default=LoreType.OTHER
    )

    class Meta(Entry.Meta):
        verbose_name = "Lore"
