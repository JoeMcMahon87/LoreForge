from django import forms

from apps.worldbook.models import Faction, Item, Location, Lore


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            "title",
            "content",
            "visibility",
            "tags",
            "lat",
            "lng",
            "region",
            "location_type",
            "parent_location",
        ]


class FactionForm(forms.ModelForm):
    class Meta:
        model = Faction
        fields = ["title", "content", "visibility", "tags", "alignment", "goals"]


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["title", "content", "visibility", "tags", "item_type", "rarity"]


class LoreForm(forms.ModelForm):
    class Meta:
        model = Lore
        fields = ["title", "content", "visibility", "tags", "lore_type"]
