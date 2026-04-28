from django.contrib import admin

from apps.worldbook.models import Faction, Item, Location, Lore, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["title", "visibility", "location_type", "region", "updated_at"]
    list_filter = ["visibility"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(Faction)
class FactionAdmin(admin.ModelAdmin):
    list_display = ["title", "visibility", "alignment", "updated_at"]
    list_filter = ["visibility"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["title", "visibility", "item_type", "rarity", "updated_at"]
    list_filter = ["visibility", "rarity"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(Lore)
class LoreAdmin(admin.ModelAdmin):
    list_display = ["title", "visibility", "lore_type", "updated_at"]
    list_filter = ["visibility", "lore_type"]
    prepopulated_fields = {"slug": ["title"]}
