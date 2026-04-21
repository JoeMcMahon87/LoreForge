from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, TemplateView, UpdateView

from apps.home.models import HomePageWidget, SiteConfig
from apps.home.registry import all_widget_types, get_widget_class
from apps.worlds.mixins import GMMixin


class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        ctx["config"] = SiteConfig.get_solo()
        ctx["widgets"] = self._visible_widgets()
        return ctx

    def _visible_widgets(self):
        user = self.request.user
        qs = HomePageWidget.objects.order_by("order")
        if user.is_authenticated and (
            hasattr(user, "is_gm") and (user.is_gm() or user.is_admin_user())
        ):
            return qs
        if user.is_authenticated:
            return qs.exclude(visibility="gm_only")
        return qs.filter(visibility="public")


class HomepageEditorView(GMMixin, TemplateView):
    template_name = "home/homepage_editor.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        ctx["widgets"] = HomePageWidget.objects.order_by("order")
        ctx["widget_types"] = all_widget_types()
        return ctx


class WidgetCreateView(GMMixin, View):
    def post(self, request):
        widget_type = request.POST.get("widget_type", "")
        widget_class = get_widget_class(widget_type)
        if not widget_class:
            return HttpResponseRedirect(reverse("homepage-editor"))
        max_order = HomePageWidget.objects.order_by("-order").values_list("order", flat=True).first()
        order = (max_order or 0) + 1
        widget = HomePageWidget.objects.create(
            widget_type=widget_type,
            order=order,
            config={},
            visibility=HomePageWidget.Visibility.PUBLIC,
        )
        if widget_class.config_form_class is not None:
            return HttpResponseRedirect(
                reverse("widget-edit", kwargs={"pk": widget.pk})
            )
        return HttpResponseRedirect(reverse("homepage-editor"))


class WidgetUpdateView(GMMixin, UpdateView):
    model = HomePageWidget
    template_name = "home/widget_edit.html"
    success_url = reverse_lazy("homepage-editor")

    def get_form_class(self):
        widget_class = get_widget_class(self.object.widget_type)
        if widget_class and widget_class.config_form_class:
            return widget_class.config_form_class
        from django import forms

        class _NullForm(forms.Form):
            pass

        return _NullForm

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        if self.request.method == "POST":
            return form_class(self.request.POST)
        return form_class(initial=self.object.config)

    def get_context_data(self, **kwargs):  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        ctx["widget"] = self.object
        ctx["visibility_choices"] = HomePageWidget.Visibility.choices
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = form_class(request.POST)
        if form.is_valid():
            self.object.config = form.cleaned_data
            visibility = request.POST.get("visibility", HomePageWidget.Visibility.PUBLIC)
            if visibility in dict(HomePageWidget.Visibility.choices):
                self.object.visibility = visibility
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        ctx = self.get_context_data(form=form)
        return self.render_to_response(ctx)


class WidgetDeleteView(GMMixin, DeleteView):
    model = HomePageWidget
    template_name = "home/widget_confirm_delete.html"
    success_url = reverse_lazy("homepage-editor")


class WidgetMoveView(GMMixin, View):
    def post(self, request, pk):
        widget = get_object_or_404(HomePageWidget, pk=pk)
        direction = request.POST.get("direction")
        widgets = list(HomePageWidget.objects.order_by("order"))
        idx = next((i for i, w in enumerate(widgets) if w.pk == widget.pk), None)
        if idx is None:
            return HttpResponseRedirect(reverse("homepage-editor"))
        if direction == "up" and idx > 0:
            other = widgets[idx - 1]
            widget.order, other.order = other.order, widget.order
            widget.save()
            other.save()
        elif direction == "down" and idx < len(widgets) - 1:
            other = widgets[idx + 1]
            widget.order, other.order = other.order, widget.order
            widget.save()
            other.save()
        return HttpResponseRedirect(reverse("homepage-editor"))
