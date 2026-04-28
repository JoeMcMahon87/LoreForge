class TestItemCRUD:
    def test_gm_can_create_item(self, client, gm_user, db):
        client.force_login(gm_user)
        response = client.post(
            "/worldbook/items/create/",
            {"title": "Staff of Power", "content": "Powerful staff.", "visibility": "gm_only", "rarity": "rare"},
        )
        assert response.status_code == 302
        assert "/worldbook/items/staff-of-power" in response["Location"]

    def test_player_cannot_create_item(self, client, player_user, db):
        client.force_login(player_user)
        response = client.post(
            "/worldbook/items/create/",
            {"title": "Stolen Gem", "visibility": "public", "rarity": "common"},
        )
        assert response.status_code == 403

    def test_gm_can_update_item(self, client, gm_user, item):
        client.force_login(gm_user)
        response = client.post(
            f"/worldbook/items/{item.slug}/edit/",
            {"title": item.title, "content": item.content, "visibility": "player", "rarity": "common"},
        )
        assert response.status_code == 302
        item.refresh_from_db()
        assert item.visibility == "player"

    def test_gm_can_delete_item(self, client, gm_user, item):
        from apps.worldbook.models import Item

        client.force_login(gm_user)
        response = client.post(f"/worldbook/items/{item.slug}/delete/")
        assert response.status_code == 302
        assert not Item.objects.filter(pk=item.pk).exists()

    def test_player_cannot_delete_item(self, client, player_user, item):
        client.force_login(player_user)
        response = client.post(f"/worldbook/items/{item.slug}/delete/")
        assert response.status_code == 403


class TestItemVisibility:
    def test_anonymous_cannot_see_gm_only_item(self, client, item):
        response = client.get(f"/worldbook/items/{item.slug}/")
        assert response.status_code == 404

    def test_anonymous_can_see_public_item(self, client, db, gm_user):
        from apps.worldbook.services import create_item

        i = create_item(title="Common Sword", visibility="public", created_by=gm_user)
        response = client.get(f"/worldbook/items/{i.slug}/")
        assert response.status_code == 200
