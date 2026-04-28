from typing import Any

from django.db.models import Model, QuerySet

from apps.worldbook.models import Faction, Item, Location, Lore


def get_visible_queryset(model_class: type[Any], user: Any) -> QuerySet[Any]:
    """Return entries visible to the requesting user based on their role."""
    if user.is_authenticated:
        if user.is_gm() or user.is_admin_user():
            return model_class.objects.all()
        return model_class.objects.filter(visibility__in=["player", "public"])
    return model_class.objects.filter(visibility="public")


def create_location(
    title: str,
    content: str = "",
    visibility: str = "gm_only",
    created_by=None,
    tags=None,
    **kwargs,
) -> Location:
    loc = Location.objects.create(
        title=title, content=content, visibility=visibility, created_by=created_by, **kwargs
    )
    if tags is not None:
        loc.tags.set(tags)
    return loc


def create_faction(
    title: str,
    content: str = "",
    visibility: str = "gm_only",
    created_by=None,
    tags=None,
    **kwargs,
) -> Faction:
    faction = Faction.objects.create(
        title=title, content=content, visibility=visibility, created_by=created_by, **kwargs
    )
    if tags is not None:
        faction.tags.set(tags)
    return faction


def create_item(
    title: str,
    content: str = "",
    visibility: str = "gm_only",
    created_by=None,
    tags=None,
    **kwargs,
) -> Item:
    item = Item.objects.create(
        title=title, content=content, visibility=visibility, created_by=created_by, **kwargs
    )
    if tags is not None:
        item.tags.set(tags)
    return item


def create_lore(
    title: str,
    content: str = "",
    visibility: str = "gm_only",
    created_by=None,
    tags=None,
    **kwargs,
) -> Lore:
    lore = Lore.objects.create(
        title=title, content=content, visibility=visibility, created_by=created_by, **kwargs
    )
    if tags is not None:
        lore.tags.set(tags)
    return lore
