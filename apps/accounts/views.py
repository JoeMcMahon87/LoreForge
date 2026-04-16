from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from apps.accounts.forms import RegistrationForm
from apps.accounts.models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(DjangoLoginView):
    template_name = "accounts/login.html"


class LogoutView(DjangoLogoutView):
    pass
