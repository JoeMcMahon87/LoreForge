import pytest
from django.urls import reverse

from apps.accounts.models import CustomUser


@pytest.mark.django_db
def test_login_page_returns_200(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_returns_200(client):
    response = client.get(reverse("register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_registration_creates_user_and_redirects(client):
    data = {
        "username": "newgm",
        "email": "newgm@example.com",
        "role": "gm",
        "password1": "Str0ng!Pass99",
        "password2": "Str0ng!Pass99",
    }
    response = client.post(reverse("register"), data)
    assert response.status_code == 302
    assert CustomUser.objects.filter(username="newgm").exists()


@pytest.mark.django_db
def test_registration_rejects_admin_role(client):
    data = {
        "username": "badactor",
        "email": "bad@example.com",
        "role": "admin",
        "password1": "Str0ng!Pass99",
        "password2": "Str0ng!Pass99",
    }
    response = client.post(reverse("register"), data)
    # Form should be invalid — admin is not a valid choice
    assert response.status_code == 200
    assert not CustomUser.objects.filter(username="badactor").exists()


@pytest.mark.django_db
def test_login_with_correct_credentials_redirects(client, gm_user):
    response = client.post(reverse("login"), {"username": "testgm", "password": "pass1234!"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_with_wrong_password_returns_form_errors(client, gm_user):
    response = client.post(reverse("login"), {"username": "testgm", "password": "wrongpassword"})
    assert response.status_code == 200
    assert response.context["form"].errors


@pytest.mark.django_db
def test_logout_redirects_to_login(client, gm_user):
    client.force_login(gm_user)
    response = client.post(reverse("logout"))
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]
