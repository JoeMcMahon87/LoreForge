from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.worlds.forms import CampaignForm, WorldConfigForm
from apps.worlds.mixins import GMMixin
from apps.worlds.models import Campaign
from apps.worlds.services import create_campaign, get_world_config

# ---------------------------------------------------------------------------
# World config views
# ---------------------------------------------------------------------------


class WorldConfigUpdateView(GMMixin, UpdateView):
    template_name = "worlds/world_settings.html"
    form_class = WorldConfigForm
    success_url = reverse_lazy("world-settings")

    def get_object(self, queryset=None):
        return get_world_config()


# ---------------------------------------------------------------------------
# Campaign views
# ---------------------------------------------------------------------------


class CampaignListView(LoginRequiredMixin, ListView):
    template_name = "worlds/campaign_list.html"
    context_object_name = "campaigns"

    def get_queryset(self):
        return Campaign.objects.order_by("created_at")


class CampaignCreateView(GMMixin, CreateView):
    template_name = "worlds/campaign_form.html"
    form_class = CampaignForm

    def form_valid(self, form):
        campaign = create_campaign(
            name=form.cleaned_data["name"],
            description=form.cleaned_data.get("description", ""),
        )
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        return HttpResponseRedirect(
            reverse("campaign-detail", kwargs={"campaign_slug": campaign.slug})
        )


class CampaignDetailView(LoginRequiredMixin, DetailView):
    template_name = "worlds/campaign_detail.html"
    context_object_name = "campaign"

    def get_object(self, queryset=None):
        return get_object_or_404(Campaign, slug=self.kwargs["campaign_slug"])


class CampaignUpdateView(GMMixin, UpdateView):
    template_name = "worlds/campaign_form.html"
    form_class = CampaignForm

    def get_object(self, queryset=None):
        return get_object_or_404(Campaign, slug=self.kwargs["campaign_slug"])

    def get_success_url(self):
        return reverse_lazy(
            "campaign-detail", kwargs={"campaign_slug": self.object.slug}
        )


class CampaignDeleteView(GMMixin, DeleteView):
    template_name = "worlds/campaign_confirm_delete.html"
    success_url = reverse_lazy("campaign-list")

    def get_object(self, queryset=None):
        return get_object_or_404(Campaign, slug=self.kwargs["campaign_slug"])
