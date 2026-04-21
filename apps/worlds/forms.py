from django import forms

from apps.worlds.models import Campaign, WorldConfig


class WorldConfigForm(forms.ModelForm):
    class Meta:
        model = WorldConfig
        fields = ["name", "tagline", "description", "theme_color", "logo"]


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "description", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # status defaults to active on create — not required when field is hidden
        self.fields["status"].required = False
