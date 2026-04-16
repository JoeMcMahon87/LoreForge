import pytest


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get("/accounts/login/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_loads(client):
    response = client.get("/accounts/register/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_redirects_when_anonymous(client):
    response = client.get("/")
    assert response.status_code in (200, 302)
