from django.urls import path

from apps.home import views

urlpatterns = [
    path("edit/", views.HomepageEditorView.as_view(), name="homepage-editor"),
    path("widgets/add/", views.WidgetCreateView.as_view(), name="widget-create"),
    path("widgets/<int:pk>/edit/", views.WidgetUpdateView.as_view(), name="widget-edit"),
    path(
        "widgets/<int:pk>/delete/",
        views.WidgetDeleteView.as_view(),
        name="widget-delete",
    ),
    path(
        "widgets/<int:pk>/move/",
        views.WidgetMoveView.as_view(),
        name="widget-move",
    ),
]
