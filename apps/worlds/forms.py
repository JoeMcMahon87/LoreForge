from django import forms

from apps.worlds.models import Campaign, World


class WorldForm(forms.ModelForm):
    class Meta:
        model = World
        fields = ["name", "description"]


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ["name", "description", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # status defaults to active on create — not required when field is hidden
        self.fields["status"].required = False
