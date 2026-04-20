import pytest
from django.test import Client

from apps.worlds.services import add_member, create_campaign, create_world


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestCampaignCreateView:
    def test_owner_can_create_campaign(self, client, gm_user):
        world = create_world(owner=gm_user, name="Faerun")
        client.force_login(gm_user)
        response = client.post(
            f"/worlds/{world.slug}/campaigns/create/",
            {"name": "Session Zero", "description": ""},
        )
        assert response.status_code == 302
        assert f"/worlds/{world.slug}/campaigns/session-zero/" in response["Location"]

    def test_player_gets_403(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Faerun")
        add_member(world=world, user=player_user, role="player")
        client.force_login(player_user)
        response = client.post(
            f"/worlds/{world.slug}/campaigns/create/",
            {"name": "Hack", "description": ""},
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestCampaignDetailView:
    def test_member_gets_200(self, client, gm_user):
        world = create_world(owner=gm_user, name="Eberron")
        campaign = create_campaign(world=world, name="The Last War")
        client.force_login(gm_user)
        response = client.get(
            f"/worlds/{world.slug}/campaigns/{campaign.slug}/"
        )
        assert response.status_code == 200

    def test_non_member_gets_403(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Eberron")
        campaign = create_campaign(world=world, name="The Last War")
        client.force_login(player_user)
        response = client.get(
            f"/worlds/{world.slug}/campaigns/{campaign.slug}/"
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestCampaignUpdateView:
    def test_owner_can_update_campaign(self, client, gm_user):
        world = create_world(owner=gm_user, name="Greyhawk")
        campaign = create_campaign(world=world, name="Old Name")
        client.force_login(gm_user)
        response = client.post(
            f"/worlds/{world.slug}/campaigns/{campaign.slug}/edit/",
            {"name": "New Name", "description": "", "status": "complete"},
        )
        assert response.status_code == 302
        campaign.refresh_from_db()
        assert campaign.name == "New Name"
        assert campaign.status == "complete"


@pytest.mark.django_db
class TestCampaignDeleteView:
    def test_owner_can_delete_campaign(self, client, gm_user):
        world = create_world(owner=gm_user, name="Ravenloft")
        campaign = create_campaign(world=world, name="Curse of Strahd")
        slug = campaign.slug
        client.force_login(gm_user)
        response = client.post(
            f"/worlds/{world.slug}/campaigns/{slug}/delete/"
        )
        assert response.status_code == 302
        assert f"/worlds/{world.slug}/" in response["Location"]
        from apps.worlds.models import Campaign
        assert not Campaign.objects.filter(slug=slug, world=world).exists()
