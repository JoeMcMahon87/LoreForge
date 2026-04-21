from django.urls import path

from apps.worlds import views

urlpatterns = [
    path("settings/", views.WorldConfigUpdateView.as_view(), name="world-settings"),
    path("campaigns/", views.CampaignListView.as_view(), name="campaign-list"),
    path("campaigns/create/", views.CampaignCreateView.as_view(), name="campaign-create"),
    path(
        "campaigns/<slug:campaign_slug>/",
        views.CampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path(
        "campaigns/<slug:campaign_slug>/edit/",
        views.CampaignUpdateView.as_view(),
        name="campaign-update",
    ),
    path(
        "campaigns/<slug:campaign_slug>/delete/",
        views.CampaignDeleteView.as_view(),
        name="campaign-delete",
    ),
]
