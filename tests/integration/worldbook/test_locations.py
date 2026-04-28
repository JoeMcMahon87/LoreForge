import pytest


@pytest.fixture
def three_locations(db, gm_user):
    from apps.worldbook.services import create_location

    gm_loc = create_location(title="GM Only Place", visibility="gm_only", created_by=gm_user)
    player_loc = create_location(title="Player Place", visibility="player", created_by=gm_user)
    public_loc = create_location(title="Public Place", visibility="public", created_by=gm_user)
    return gm_loc, player_loc, public_loc


class TestLocationListView:
    def test_anonymous_sees_only_public_entries(self, client, three_locations):
        response = client.get("/worldbook/locations/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Public Place" in content
        assert "Player Place" not in content
        assert "GM Only Place" not in content

    def test_player_sees_public_and_player_entries(self, client, player_user, three_locations):
        client.force_login(player_user)
        response = client.get("/worldbook/locations/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Public Place" in content
        assert "Player Place" in content
        assert "GM Only Place" not in content

    def test_gm_sees_all_entries(self, client, gm_user, three_locations):
        client.force_login(gm_user)
        response = client.get("/worldbook/locations/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "GM Only Place" in content
        assert "Player Place" in content
        assert "Public Place" in content

    def test_empty_state_renders(self, client, db):
        response = client.get("/worldbook/locations/")
        assert response.status_code == 200
        assert "No locations yet." in response.content.decode()


class TestLocationDetailView:
    def test_gm_can_view_gm_only_entry(self, client, gm_user, location):
        client.force_login(gm_user)
        response = client.get(f"/worldbook/locations/{location.slug}/")
        assert response.status_code == 200
        assert location.title in response.content.decode()

    def test_player_cannot_access_gm_only_entry_gets_404(self, client, player_user, location):
        client.force_login(player_user)
        response = client.get(f"/worldbook/locations/{location.slug}/")
        assert response.status_code == 404

    def test_anonymous_cannot_access_player_entry_gets_404(self, client, db, gm_user):
        from apps.worldbook.services import create_location

        loc = create_location(title="Player Visible", visibility="player", created_by=gm_user)
        response = client.get(f"/worldbook/locations/{loc.slug}/")
        assert response.status_code == 404

    def test_anonymous_can_view_public_entry(self, client, db, gm_user):
        from apps.worldbook.services import create_location

        loc = create_location(title="Public Spot", visibility="public", created_by=gm_user)
        response = client.get(f"/worldbook/locations/{loc.slug}/")
        assert response.status_code == 200
        assert "Public Spot" in response.content.decode()


class TestLocationCreateView:
    def test_gm_can_create_location(self, client, gm_user, db):
        client.force_login(gm_user)
        response = client.post(
            "/worldbook/locations/create/",
            {"title": "New Dungeon", "content": "Dark and deep.", "visibility": "gm_only"},
        )
        assert response.status_code == 302
        assert response["Location"].startswith("/worldbook/locations/new-dungeon")

    def test_player_gets_403(self, client, player_user, db):
        client.force_login(player_user)
        response = client.post(
            "/worldbook/locations/create/",
            {"title": "Sneaky Spot", "visibility": "public"},
        )
        assert response.status_code == 403

    def test_anonymous_redirects_to_login(self, client, db):
        response = client.post(
            "/worldbook/locations/create/",
            {"title": "Somewhere", "visibility": "public"},
        )
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


class TestLocationUpdateView:
    def test_gm_can_update_location(self, client, gm_user, location):
        client.force_login(gm_user)
        response = client.post(
            f"/worldbook/locations/{location.slug}/edit/",
            {"title": location.title, "content": "Updated content.", "visibility": "player"},
        )
        assert response.status_code == 302
        location.refresh_from_db()
        assert location.visibility == "player"

    def test_player_gets_403(self, client, player_user, location):
        client.force_login(player_user)
        response = client.post(
            f"/worldbook/locations/{location.slug}/edit/",
            {"title": location.title, "visibility": "public"},
        )
        assert response.status_code == 403


class TestLocationDeleteView:
    def test_gm_can_delete_location(self, client, gm_user, location):
        from apps.worldbook.models import Location

        client.force_login(gm_user)
        response = client.post(f"/worldbook/locations/{location.slug}/delete/")
        assert response.status_code == 302
        assert not Location.objects.filter(pk=location.pk).exists()

    def test_player_gets_403(self, client, player_user, location):
        client.force_login(player_user)
        response = client.post(f"/worldbook/locations/{location.slug}/delete/")
        assert response.status_code == 403
