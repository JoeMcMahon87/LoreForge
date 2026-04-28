class TestFactionCRUD:
    def test_gm_can_create_faction(self, client, gm_user, db):
        client.force_login(gm_user)
        response = client.post(
            "/worldbook/factions/create/",
            {"title": "The Crimson Order", "content": "A secretive group.", "visibility": "gm_only"},
        )
        assert response.status_code == 302
        assert "/worldbook/factions/the-crimson-order" in response["Location"]

    def test_player_cannot_create_faction(self, client, player_user, db):
        client.force_login(player_user)
        response = client.post(
            "/worldbook/factions/create/",
            {"title": "Rebel Group", "visibility": "public"},
        )
        assert response.status_code == 403

    def test_gm_can_update_faction(self, client, gm_user, faction):
        client.force_login(gm_user)
        response = client.post(
            f"/worldbook/factions/{faction.slug}/edit/",
            {"title": faction.title, "content": faction.content, "visibility": "player"},
        )
        assert response.status_code == 302
        faction.refresh_from_db()
        assert faction.visibility == "player"

    def test_gm_can_delete_faction(self, client, gm_user, faction):
        from apps.worldbook.models import Faction

        client.force_login(gm_user)
        response = client.post(f"/worldbook/factions/{faction.slug}/delete/")
        assert response.status_code == 302
        assert not Faction.objects.filter(pk=faction.pk).exists()

    def test_player_cannot_delete_faction(self, client, player_user, faction):
        client.force_login(player_user)
        response = client.post(f"/worldbook/factions/{faction.slug}/delete/")
        assert response.status_code == 403


class TestFactionVisibility:
    def test_anonymous_cannot_see_gm_only_faction(self, client, faction):
        response = client.get(f"/worldbook/factions/{faction.slug}/")
        assert response.status_code == 404

    def test_anonymous_can_see_public_faction(self, client, db, gm_user):
        from apps.worldbook.services import create_faction

        f = create_faction(title="Public Faction", visibility="public", created_by=gm_user)
        response = client.get(f"/worldbook/factions/{f.slug}/")
        assert response.status_code == 200
