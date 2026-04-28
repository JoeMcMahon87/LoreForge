class TestLoreCRUD:
    def test_gm_can_create_lore(self, client, gm_user, db):
        client.force_login(gm_user)
        response = client.post(
            "/worldbook/lore/create/",
            {
                "title": "The Great Cataclysm",
                "content": "Ages ago...",
                "visibility": "gm_only",
                "lore_type": "history",
            },
        )
        assert response.status_code == 302
        assert "/worldbook/lore/the-great-cataclysm" in response["Location"]

    def test_player_cannot_create_lore(self, client, player_user, db):
        client.force_login(player_user)
        response = client.post(
            "/worldbook/lore/create/",
            {"title": "Player Tale", "visibility": "public", "lore_type": "myth"},
        )
        assert response.status_code == 403

    def test_gm_can_update_lore(self, client, gm_user, lore):
        client.force_login(gm_user)
        response = client.post(
            f"/worldbook/lore/{lore.slug}/edit/",
            {"title": lore.title, "content": lore.content, "visibility": "player", "lore_type": lore.lore_type},
        )
        assert response.status_code == 302
        lore.refresh_from_db()
        assert lore.visibility == "player"

    def test_gm_can_delete_lore(self, client, gm_user, lore):
        from apps.worldbook.models import Lore

        client.force_login(gm_user)
        response = client.post(f"/worldbook/lore/{lore.slug}/delete/")
        assert response.status_code == 302
        assert not Lore.objects.filter(pk=lore.pk).exists()

    def test_player_cannot_delete_lore(self, client, player_user, lore):
        client.force_login(player_user)
        response = client.post(f"/worldbook/lore/{lore.slug}/delete/")
        assert response.status_code == 403


class TestLoreVisibility:
    def test_anonymous_cannot_see_gm_only_lore(self, client, lore):
        response = client.get(f"/worldbook/lore/{lore.slug}/")
        assert response.status_code == 404

    def test_anonymous_can_see_public_lore(self, client, db, gm_user):
        from apps.worldbook.services import create_lore

        entry = create_lore(title="Ancient Legend", visibility="public", created_by=gm_user)
        response = client.get(f"/worldbook/lore/{entry.slug}/")
        assert response.status_code == 200
