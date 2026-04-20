import pytest
from django.test import Client

from apps.home.models import SiteConfig


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestHomePage:
    def test_anonymous_gets_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_authenticated_gets_200(self, client, gm_user):
        client.force_login(gm_user)
        response = client.get("/")
        assert response.status_code == 200

    def test_renders_hero_title(self, client):
        config = SiteConfig.get_solo()
        response = client.get("/")
        assert config.hero_title.encode() in response.content

    def test_updated_hero_title_appears(self, client):
        config = SiteConfig.get_solo()
        config.hero_title = "Welcome to the New World"
        config.save()
        response = client.get("/")
        assert b"Welcome to the New World" in response.content
