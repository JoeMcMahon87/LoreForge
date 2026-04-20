from django.contrib import admin

from apps.worlds.models import Campaign, World, WorldMembership


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "owner", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "world", "status", "created_at"]
    list_filter = ["status", "world"]


@admin.register(WorldMembership)
class WorldMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "world", "role"]
    list_filter = ["role", "world"]
