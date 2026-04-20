from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.worlds.forms import CampaignForm, WorldForm
from apps.worlds.mixins import GMMixin, WorldMemberMixin, WorldOwnerMixin
from apps.worlds.models import Campaign, World
from apps.worlds.services import (
    create_campaign,
    create_world,
    get_worlds_for_user,
)

# ---------------------------------------------------------------------------
# World views
# ---------------------------------------------------------------------------


class WorldListView(LoginRequiredMixin, ListView):
    template_name = "worlds/world_list.html"
    context_object_name = "worlds"

    def get_queryset(self):
        return get_worlds_for_user(self.request.user)


class WorldDetailView(WorldMemberMixin, DetailView):
    template_name = "worlds/world_detail.html"
    context_object_name = "world"

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return self.get_world()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["campaigns"] = self.object.campaigns.all()
        ctx["memberships"] = self.object.memberships.select_related("user")
        return ctx


class WorldCreateView(GMMixin, CreateView):
    template_name = "worlds/world_form.html"
    form_class = WorldForm

    def form_valid(self, form):
        world = create_world(
            owner=self.request.user,
            name=form.cleaned_data["name"],
            description=form.cleaned_data.get("description", ""),
        )
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(reverse("world-detail", kwargs={"world_slug": world.slug}))


class WorldUpdateView(WorldOwnerMixin, UpdateView):
    template_name = "worlds/world_form.html"
    form_class = WorldForm
    slug_field = "slug"
    slug_url_kwarg = "world_slug"

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return self.get_world()

    def get_success_url(self):
        return reverse_lazy("world-detail", kwargs={"world_slug": self.object.slug})


class WorldDeleteView(WorldOwnerMixin, DeleteView):
    template_name = "worlds/world_confirm_delete.html"
    success_url = reverse_lazy("world-list")

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return self.get_world()


# ---------------------------------------------------------------------------
# Campaign views
# ---------------------------------------------------------------------------


class CampaignCreateView(WorldOwnerMixin, CreateView):
    template_name = "worlds/campaign_form.html"
    form_class = CampaignForm

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["world"] = self.get_world()
        return ctx

    def form_valid(self, form):
        world = self.get_world()
        campaign = create_campaign(
            world=world,
            name=form.cleaned_data["name"],
            description=form.cleaned_data.get("description", ""),
        )
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        return HttpResponseRedirect(
            reverse(
                "campaign-detail",
                kwargs={"world_slug": world.slug, "campaign_slug": campaign.slug},
            )
        )


class CampaignDetailView(WorldMemberMixin, DetailView):
    template_name = "worlds/campaign_detail.html"
    context_object_name = "campaign"

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return get_object_or_404(
            Campaign,
            slug=self.kwargs["campaign_slug"],
            world=self.get_world(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["world"] = self.get_world()
        return ctx


class CampaignUpdateView(WorldOwnerMixin, UpdateView):
    template_name = "worlds/campaign_form.html"
    form_class = CampaignForm

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return get_object_or_404(
            Campaign,
            slug=self.kwargs["campaign_slug"],
            world=self.get_world(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["world"] = self.get_world()
        return ctx

    def get_success_url(self):
        world = self.get_world()
        return reverse_lazy(
            "campaign-detail",
            kwargs={"world_slug": world.slug, "campaign_slug": self.object.slug},
        )


class CampaignDeleteView(WorldOwnerMixin, DeleteView):
    template_name = "worlds/campaign_confirm_delete.html"

    def get_world(self):
        return get_object_or_404(World, slug=self.kwargs["world_slug"])

    def get_object(self, queryset=None):
        return get_object_or_404(
            Campaign,
            slug=self.kwargs["campaign_slug"],
            world=self.get_world(),
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["world"] = self.get_world()
        return ctx

    def get_success_url(self):
        world = self.get_world()
        return reverse_lazy("world-detail", kwargs={"world_slug": world.slug})
