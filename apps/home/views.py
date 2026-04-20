from django.views.generic import TemplateView

from apps.home.models import SiteConfig


class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        ctx["config"] = SiteConfig.get_solo()
        return ctx
