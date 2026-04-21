from django.contrib import admin

from apps.worlds.models import Campaign, WorldConfig


@admin.register(WorldConfig)
class WorldConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "tagline", "theme_color", "updated_at"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "status", "created_at"]
    list_filter = ["status"]
    prepopulated_fields = {"slug": ("name",)}
