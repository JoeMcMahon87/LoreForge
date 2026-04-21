import pytest
from django.test import Client

from apps.worlds.services import create_campaign


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestCampaignCreateView:
    def test_gm_can_create_campaign(self, client, gm_user):
        client.force_login(gm_user)
        response = client.post(
            "/world/campaigns/create/",
            {"name": "Session Zero", "description": ""},
        )
        assert response.status_code == 302
        assert "/world/campaigns/session-zero/" in response["Location"]

    def test_player_gets_403(self, client, player_user):
        client.force_login(player_user)
        response = client.post(
            "/world/campaigns/create/",
            {"name": "Hack", "description": ""},
        )
        assert response.status_code == 403

    def test_anonymous_redirects_to_login(self, client):
        response = client.post(
            "/world/campaigns/create/",
            {"name": "Session Zero", "description": ""},
        )
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
class TestCampaignDetailView:
    def test_authenticated_user_gets_200(self, client, gm_user):
        campaign = create_campaign(name="The Last War")
        client.force_login(gm_user)
        response = client.get(f"/world/campaigns/{campaign.slug}/")
        assert response.status_code == 200

    def test_player_gets_200(self, client, player_user):
        campaign = create_campaign(name="The Last War")
        client.force_login(player_user)
        response = client.get(f"/world/campaigns/{campaign.slug}/")
        assert response.status_code == 200

    def test_anonymous_redirects_to_login(self, client):
        campaign = create_campaign(name="The Last War")
        response = client.get(f"/world/campaigns/{campaign.slug}/")
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
class TestCampaignUpdateView:
    def test_gm_can_update_campaign(self, client, gm_user):
        campaign = create_campaign(name="Old Name")
        client.force_login(gm_user)
        response = client.post(
            f"/world/campaigns/{campaign.slug}/edit/",
            {"name": "New Name", "description": "", "status": "complete"},
        )
        assert response.status_code == 302
        campaign.refresh_from_db()
        assert campaign.name == "New Name"
        assert campaign.status == "complete"

    def test_player_gets_403(self, client, player_user):
        campaign = create_campaign(name="My Campaign")
        client.force_login(player_user)
        response = client.post(
            f"/world/campaigns/{campaign.slug}/edit/",
            {"name": "Hacked", "description": ""},
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestCampaignDeleteView:
    def test_gm_can_delete_campaign(self, client, gm_user):
        campaign = create_campaign(name="Curse of Strahd")
        slug = campaign.slug
        client.force_login(gm_user)
        response = client.post(f"/world/campaigns/{slug}/delete/")
        assert response.status_code == 302
        assert "/world/campaigns/" in response["Location"]
        from apps.worlds.models import Campaign
        assert not Campaign.objects.filter(slug=slug).exists()

    def test_player_gets_403(self, client, player_user):
        campaign = create_campaign(name="My Campaign")
        client.force_login(player_user)
        response = client.post(f"/world/campaigns/{campaign.slug}/delete/")
        assert response.status_code == 403
