from apps.home.widgets import (
    CampaignListWidget,
    ImageBannerWidget,
    RecentEntriesWidget,
    RichTextWidget,
)

_REGISTRY: dict = {}


def _register(widget_class) -> None:
    _REGISTRY[widget_class.type_slug] = widget_class


_register(RichTextWidget)
_register(CampaignListWidget)
_register(RecentEntriesWidget)
_register(ImageBannerWidget)


def get_widget_class(type_slug: str):
    return _REGISTRY.get(type_slug)


def all_widget_types() -> list:
    return list(_REGISTRY.values())
