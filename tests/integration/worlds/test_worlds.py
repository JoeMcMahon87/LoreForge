import pytest
from django.test import Client

from apps.worlds.services import add_member, create_world


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestWorldListView:
    def test_anonymous_redirects_to_login(self, client):
        response = client.get("/worlds/")
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_gm_sees_their_worlds(self, client, gm_user):
        create_world(owner=gm_user, name="Faerun")
        client.force_login(gm_user)
        response = client.get("/worlds/")
        assert response.status_code == 200
        assert b"Faerun" in response.content

    def test_player_sees_member_worlds(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Eberron")
        add_member(world=world, user=player_user, role="player")
        client.force_login(player_user)
        response = client.get("/worlds/")
        assert response.status_code == 200
        assert b"Eberron" in response.content


@pytest.mark.django_db
class TestWorldCreateView:
    def test_gm_can_create_world(self, client, gm_user):
        client.force_login(gm_user)
        response = client.post("/worlds/create/", {"name": "Greyhawk", "description": ""})
        assert response.status_code == 302
        assert "/worlds/greyhawk/" in response["Location"]

    def test_player_gets_403(self, client, player_user):
        client.force_login(player_user)
        response = client.post("/worlds/create/", {"name": "Greyhawk", "description": ""})
        assert response.status_code == 403


@pytest.mark.django_db
class TestWorldDetailView:
    def test_member_gets_200(self, client, gm_user):
        world = create_world(owner=gm_user, name="Ravenloft")
        client.force_login(gm_user)
        response = client.get(f"/worlds/{world.slug}/")
        assert response.status_code == 200

    def test_non_member_gets_403(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Ravenloft")
        client.force_login(player_user)
        response = client.get(f"/worlds/{world.slug}/")
        assert response.status_code == 403

    def test_anonymous_redirects_to_login(self, client, gm_user):
        world = create_world(owner=gm_user, name="Ravenloft")
        response = client.get(f"/worlds/{world.slug}/")
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
class TestWorldUpdateView:
    def test_owner_can_update(self, client, gm_user):
        world = create_world(owner=gm_user, name="Old Name")
        client.force_login(gm_user)
        response = client.post(
            f"/worlds/{world.slug}/edit/",
            {"name": "New Name", "description": ""},
        )
        assert response.status_code == 302
        world.refresh_from_db()
        assert world.name == "New Name"

    def test_player_gets_403(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="My World")
        add_member(world=world, user=player_user, role="player")
        client.force_login(player_user)
        response = client.post(
            f"/worlds/{world.slug}/edit/",
            {"name": "Hacked", "description": ""},
        )
        assert response.status_code == 403


@pytest.mark.django_db
class TestWorldDeleteView:
    def test_owner_can_delete(self, client, gm_user):
        world = create_world(owner=gm_user, name="Doomed World")
        slug = world.slug
        client.force_login(gm_user)
        response = client.post(f"/worlds/{slug}/delete/")
        assert response.status_code == 302
        from apps.worlds.models import World
        assert not World.objects.filter(slug=slug).exists()

    def test_non_owner_gets_403(self, client, gm_user, player_user):
        world = create_world(owner=gm_user, name="Protected World")
        add_member(world=world, user=player_user, role="player")
        client.force_login(player_user)
        response = client.post(f"/worlds/{world.slug}/delete/")
        assert response.status_code == 403
