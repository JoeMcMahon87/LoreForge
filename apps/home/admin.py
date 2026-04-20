from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from apps.home.models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):  # type: ignore[override]
        return not SiteConfig.objects.exists()

    def changelist_view(self, request, extra_context=None):  # type: ignore[override]
        config = SiteConfig.get_solo()
        return HttpResponseRedirect(
            reverse("admin:home_siteconfig_change", args=[config.pk])
        )
