import pytest
from django.test import Client

from apps.worlds.models import WorldMembership
from apps.worlds.services import add_member, create_world


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestMembership:
    def test_owner_is_gm_member_after_create(self, gm_user):
        world = create_world(owner=gm_user, name="Test World")
        assert WorldMembership.objects.filter(
            user=gm_user, world=world, role=WorldMembership.Role.GM
        ).exists()

    def test_player_can_access_world_after_add_member(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Accessible World")
        add_member(world=world, user=player_user, role="player")
        client.force_login(player_user)
        response = client.get(f"/worlds/{world.slug}/")
        assert response.status_code == 200

    def test_non_member_gets_403_on_world_detail(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Private World")
        client.force_login(player_user)
        response = client.get(f"/worlds/{world.slug}/")
        assert response.status_code == 403
