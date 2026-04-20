from django.urls import path

from apps.worlds import views

urlpatterns = [
    path("", views.WorldListView.as_view(), name="world-list"),
    path("create/", views.WorldCreateView.as_view(), name="world-create"),
    path("<slug:world_slug>/", views.WorldDetailView.as_view(), name="world-detail"),
    path("<slug:world_slug>/edit/", views.WorldUpdateView.as_view(), name="world-update"),
    path("<slug:world_slug>/delete/", views.WorldDeleteView.as_view(), name="world-delete"),
    path(
        "<slug:world_slug>/campaigns/create/",
        views.CampaignCreateView.as_view(),
        name="campaign-create",
    ),
    path(
        "<slug:world_slug>/campaigns/<slug:campaign_slug>/",
        views.CampaignDetailView.as_view(),
        name="campaign-detail",
    ),
    path(
        "<slug:world_slug>/campaigns/<slug:campaign_slug>/edit/",
        views.CampaignUpdateView.as_view(),
        name="campaign-update",
    ),
    path(
        "<slug:world_slug>/campaigns/<slug:campaign_slug>/delete/",
        views.CampaignDeleteView.as_view(),
        name="campaign-delete",
    ),
]
