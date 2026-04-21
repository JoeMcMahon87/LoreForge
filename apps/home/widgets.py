from __future__ import annotations

from django import forms


class BaseWidget:
    type_slug: str = ""
    label: str = ""
    template_name: str = ""
    config_form_class: type[forms.Form] | None = None

    @classmethod
    def get_context(cls, config: dict) -> dict:
        return {"config": config}


class RichTextConfigForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 8}), required=False)


class RichTextWidget(BaseWidget):
    type_slug = "rich_text"
    label = "Rich Text"
    template_name = "home/widgets/rich_text.html"
    config_form_class = RichTextConfigForm

    @classmethod
    def get_context(cls, config: dict) -> dict:
        return {"content": config.get("content", "")}


class CampaignListWidget(BaseWidget):
    type_slug = "campaign_list"
    label = "Campaign List"
    template_name = "home/widgets/campaign_list.html"

    @classmethod
    def get_context(cls, config: dict) -> dict:
        from apps.worlds.models import Campaign

        return {"campaigns": Campaign.objects.order_by("created_at")}


class RecentEntriesConfigForm(forms.Form):
    count = forms.IntegerField(min_value=1, max_value=20, initial=5)


class RecentEntriesWidget(BaseWidget):
    type_slug = "recent_entries"
    label = "Recent Entries"
    template_name = "home/widgets/recent_entries.html"
    config_form_class = RecentEntriesConfigForm

    @classmethod
    def get_context(cls, config: dict) -> dict:
        return {"entries": [], "count": config.get("count", 5)}


class ImageBannerConfigForm(forms.Form):
    image_url = forms.URLField(required=False, assume_scheme="https")
    alt = forms.CharField(max_length=200, required=False)
    caption = forms.CharField(max_length=400, required=False)


class ImageBannerWidget(BaseWidget):
    type_slug = "image_banner"
    label = "Image Banner"
    template_name = "home/widgets/image_banner.html"
    config_form_class = ImageBannerConfigForm

    @classmethod
    def get_context(cls, config: dict) -> dict:
        return {
            "image_url": config.get("image_url", ""),
            "alt": config.get("alt", ""),
            "caption": config.get("caption", ""),
        }
