from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.worldbook.forms import FactionForm, ItemForm, LocationForm, LoreForm
from apps.worldbook.models import Faction, Item, Location, Lore
from apps.worldbook.services import get_visible_queryset
from apps.worlds.mixins import GMMixin

# ---------------------------------------------------------------------------
# Location views
# ---------------------------------------------------------------------------


class LocationListView(ListView):
    template_name = "worldbook/location_list.html"
    context_object_name = "entries"

    def get_queryset(self):
        return get_visible_queryset(Location, self.request.user)


class LocationDetailView(DetailView):
    template_name = "worldbook/location_detail.html"
    context_object_name = "entry"

    def get_object(self, queryset=None):
        qs = get_visible_queryset(Location, self.request.user)
        return get_object_or_404(qs, slug=self.kwargs["entry_slug"])


class LocationCreateView(GMMixin, CreateView):
    template_name = "worldbook/location_form.html"
    form_class = LocationForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse("location-detail", kwargs={"entry_slug": obj.slug}))


class LocationUpdateView(GMMixin, UpdateView):
    template_name = "worldbook/location_form.html"
    form_class = LocationForm

    def get_object(self, queryset=None):
        return get_object_or_404(Location, slug=self.kwargs["entry_slug"])

    def get_success_url(self):
        return reverse_lazy("location-detail", kwargs={"entry_slug": self.object.slug})


class LocationDeleteView(GMMixin, DeleteView):
    template_name = "worldbook/location_confirm_delete.html"
    success_url = reverse_lazy("location-list")

    def get_object(self, queryset=None):
        return get_object_or_404(Location, slug=self.kwargs["entry_slug"])


# ---------------------------------------------------------------------------
# Faction views
# ---------------------------------------------------------------------------


class FactionListView(ListView):
    template_name = "worldbook/faction_list.html"
    context_object_name = "entries"

    def get_queryset(self):
        return get_visible_queryset(Faction, self.request.user)


class FactionDetailView(DetailView):
    template_name = "worldbook/faction_detail.html"
    context_object_name = "entry"

    def get_object(self, queryset=None):
        qs = get_visible_queryset(Faction, self.request.user)
        return get_object_or_404(qs, slug=self.kwargs["entry_slug"])


class FactionCreateView(GMMixin, CreateView):
    template_name = "worldbook/faction_form.html"
    form_class = FactionForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse("faction-detail", kwargs={"entry_slug": obj.slug}))


class FactionUpdateView(GMMixin, UpdateView):
    template_name = "worldbook/faction_form.html"
    form_class = FactionForm

    def get_object(self, queryset=None):
        return get_object_or_404(Faction, slug=self.kwargs["entry_slug"])

    def get_success_url(self):
        return reverse_lazy("faction-detail", kwargs={"entry_slug": self.object.slug})


class FactionDeleteView(GMMixin, DeleteView):
    template_name = "worldbook/faction_confirm_delete.html"
    success_url = reverse_lazy("faction-list")

    def get_object(self, queryset=None):
        return get_object_or_404(Faction, slug=self.kwargs["entry_slug"])


# ---------------------------------------------------------------------------
# Item views
# ---------------------------------------------------------------------------


class ItemListView(ListView):
    template_name = "worldbook/item_list.html"
    context_object_name = "entries"

    def get_queryset(self):
        return get_visible_queryset(Item, self.request.user)


class ItemDetailView(DetailView):
    template_name = "worldbook/item_detail.html"
    context_object_name = "entry"

    def get_object(self, queryset=None):
        qs = get_visible_queryset(Item, self.request.user)
        return get_object_or_404(qs, slug=self.kwargs["entry_slug"])


class ItemCreateView(GMMixin, CreateView):
    template_name = "worldbook/item_form.html"
    form_class = ItemForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse("item-detail", kwargs={"entry_slug": obj.slug}))


class ItemUpdateView(GMMixin, UpdateView):
    template_name = "worldbook/item_form.html"
    form_class = ItemForm

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs["entry_slug"])

    def get_success_url(self):
        return reverse_lazy("item-detail", kwargs={"entry_slug": self.object.slug})


class ItemDeleteView(GMMixin, DeleteView):
    template_name = "worldbook/item_confirm_delete.html"
    success_url = reverse_lazy("item-list")

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs["entry_slug"])


# ---------------------------------------------------------------------------
# Lore views
# ---------------------------------------------------------------------------


class LoreListView(ListView):
    template_name = "worldbook/lore_list.html"
    context_object_name = "entries"

    def get_queryset(self):
        return get_visible_queryset(Lore, self.request.user)


class LoreDetailView(DetailView):
    template_name = "worldbook/lore_detail.html"
    context_object_name = "entry"

    def get_object(self, queryset=None):
        qs = get_visible_queryset(Lore, self.request.user)
        return get_object_or_404(qs, slug=self.kwargs["entry_slug"])


class LoreCreateView(GMMixin, CreateView):
    template_name = "worldbook/lore_form.html"
    form_class = LoreForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        form.save_m2m()
        return HttpResponseRedirect(reverse("lore-detail", kwargs={"entry_slug": obj.slug}))


class LoreUpdateView(GMMixin, UpdateView):
    template_name = "worldbook/lore_form.html"
    form_class = LoreForm

    def get_object(self, queryset=None):
        return get_object_or_404(Lore, slug=self.kwargs["entry_slug"])

    def get_success_url(self):
        return reverse_lazy("lore-detail", kwargs={"entry_slug": self.object.slug})


class LoreDeleteView(GMMixin, DeleteView):
    template_name = "worldbook/lore_confirm_delete.html"
    success_url = reverse_lazy("lore-list")

    def get_object(self, queryset=None):
        return get_object_or_404(Lore, slug=self.kwargs["entry_slug"])
