from django.urls import path

from apps.worldbook import views

urlpatterns = [
    # Locations
    path("locations/", views.LocationListView.as_view(), name="location-list"),
    path("locations/create/", views.LocationCreateView.as_view(), name="location-create"),
    path("locations/<slug:entry_slug>/", views.LocationDetailView.as_view(), name="location-detail"),
    path("locations/<slug:entry_slug>/edit/", views.LocationUpdateView.as_view(), name="location-update"),
    path("locations/<slug:entry_slug>/delete/", views.LocationDeleteView.as_view(), name="location-delete"),
    # Factions
    path("factions/", views.FactionListView.as_view(), name="faction-list"),
    path("factions/create/", views.FactionCreateView.as_view(), name="faction-create"),
    path("factions/<slug:entry_slug>/", views.FactionDetailView.as_view(), name="faction-detail"),
    path("factions/<slug:entry_slug>/edit/", views.FactionUpdateView.as_view(), name="faction-update"),
    path("factions/<slug:entry_slug>/delete/", views.FactionDeleteView.as_view(), name="faction-delete"),
    # Items
    path("items/", views.ItemListView.as_view(), name="item-list"),
    path("items/create/", views.ItemCreateView.as_view(), name="item-create"),
    path("items/<slug:entry_slug>/", views.ItemDetailView.as_view(), name="item-detail"),
    path("items/<slug:entry_slug>/edit/", views.ItemUpdateView.as_view(), name="item-update"),
    path("items/<slug:entry_slug>/delete/", views.ItemDeleteView.as_view(), name="item-delete"),
    # Lore
    path("lore/", views.LoreListView.as_view(), name="lore-list"),
    path("lore/create/", views.LoreCreateView.as_view(), name="lore-create"),
    path("lore/<slug:entry_slug>/", views.LoreDetailView.as_view(), name="lore-detail"),
    path("lore/<slug:entry_slug>/edit/", views.LoreUpdateView.as_view(), name="lore-update"),
    path("lore/<slug:entry_slug>/delete/", views.LoreDeleteView.as_view(), name="lore-delete"),
]
