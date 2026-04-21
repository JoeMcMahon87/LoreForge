import pytest
from django.test import Client

from apps.worlds.models import WorldConfig


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestWorldConfigUpdateView:
    def test_anonymous_redirects_to_login(self, client):
        response = client.get("/world/settings/")
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_gm_can_view_settings(self, client, gm_user):
        client.force_login(gm_user)
        response = client.get("/world/settings/")
        assert response.status_code == 200

    def test_player_gets_403(self, client, player_user):
        client.force_login(player_user)
        response = client.get("/world/settings/")
        assert response.status_code == 403

    def test_gm_can_update_world_name(self, client, gm_user):
        client.force_login(gm_user)
        response = client.post(
            "/world/settings/",
            {"name": "Faerun", "tagline": "", "description": "", "theme_color": "#4f46e5"},
        )
        assert response.status_code == 302
        config = WorldConfig.get_solo()
        assert config.name == "Faerun"

    def test_player_cannot_update_settings(self, client, player_user):
        client.force_login(player_user)
        response = client.post(
            "/world/settings/",
            {"name": "Hacked", "tagline": "", "description": "", "theme_color": "#000000"},
        )
        assert response.status_code == 403
        config = WorldConfig.get_solo()
        assert config.name != "Hacked"
