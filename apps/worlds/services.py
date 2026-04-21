from django.db.models import QuerySet

from apps.worlds.models import Campaign, WorldConfig


def get_world_config() -> WorldConfig:
    return WorldConfig.get_solo()


def update_world_config(
    name: str,
    tagline: str = "",
    description: str = "",
    theme_color: str = "#4f46e5",
    logo=None,
) -> WorldConfig:
    config = WorldConfig.get_solo()
    config.name = name
    config.tagline = tagline
    config.description = description
    config.theme_color = theme_color
    if logo is not None:
        config.logo = logo
    config.save()
    return config


def get_all_campaigns() -> QuerySet:
    return Campaign.objects.order_by("created_at")


def create_campaign(name: str, description: str = "") -> Campaign:
    return Campaign.objects.create(name=name, description=description)
