import pytest

from apps.home.registry import all_widget_types, get_widget_class
from apps.home.widgets import (
    CampaignListWidget,
    ImageBannerWidget,
    RecentEntriesWidget,
    RichTextWidget,
)


class TestWidgetRegistry:
    def test_all_core_widgets_registered(self):
        slugs = {w.type_slug for w in all_widget_types()}
        assert {"rich_text", "campaign_list", "recent_entries", "image_banner"} <= slugs

    def test_get_widget_class_by_slug(self):
        assert get_widget_class("rich_text") is RichTextWidget
        assert get_widget_class("campaign_list") is CampaignListWidget
        assert get_widget_class("recent_entries") is RecentEntriesWidget
        assert get_widget_class("image_banner") is ImageBannerWidget

    def test_unknown_slug_returns_none(self):
        assert get_widget_class("does_not_exist") is None

    def test_each_widget_has_required_attributes(self):
        for widget_class in all_widget_types():
            assert hasattr(widget_class, "type_slug") and widget_class.type_slug
            assert hasattr(widget_class, "label") and widget_class.label
            assert hasattr(widget_class, "template_name") and widget_class.template_name
            assert hasattr(widget_class, "get_context")

    @pytest.mark.django_db
    def test_campaign_list_widget_get_context_returns_campaigns(self):
        from apps.worlds.services import create_campaign

        create_campaign(name="Test Campaign")
        ctx = CampaignListWidget.get_context({})
        assert "campaigns" in ctx
        assert ctx["campaigns"].count() == 1

    def test_rich_text_widget_get_context_returns_content(self):
        ctx = RichTextWidget.get_context({"content": "<p>Hello</p>"})
        assert ctx["content"] == "<p>Hello</p>"

    def test_image_banner_widget_get_context(self):
        ctx = ImageBannerWidget.get_context(
            {"image_url": "http://example.com/img.png", "alt": "Banner", "caption": ""}
        )
        assert ctx["image_url"] == "http://example.com/img.png"
        assert ctx["alt"] == "Banner"
