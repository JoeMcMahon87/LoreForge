import pytest
from django.test import Client

from apps.home.models import HomePageWidget


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestHomepageEditorView:
    def test_anonymous_redirects_to_login(self, client):
        response = client.get("/homepage/edit/")
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_player_gets_403(self, client, player_user):
        client.force_login(player_user)
        response = client.get("/homepage/edit/")
        assert response.status_code == 403

    def test_gm_can_access_editor(self, client, gm_user):
        client.force_login(gm_user)
        response = client.get("/homepage/edit/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestWidgetCreateView:
    def test_gm_can_add_widget(self, client, gm_user):
        client.force_login(gm_user)
        response = client.post("/homepage/widgets/add/", {"widget_type": "rich_text"})
        assert response.status_code == 302
        assert HomePageWidget.objects.filter(widget_type="rich_text").exists()

    def test_player_cannot_add_widget(self, client, player_user):
        client.force_login(player_user)
        response = client.post("/homepage/widgets/add/", {"widget_type": "rich_text"})
        assert response.status_code == 403

    def test_invalid_widget_type_redirects_to_editor(self, client, gm_user):
        client.force_login(gm_user)
        response = client.post("/homepage/widgets/add/", {"widget_type": "nonexistent"})
        assert response.status_code == 302
        assert "edit" in response["Location"]
        assert not HomePageWidget.objects.filter(widget_type="nonexistent").exists()


@pytest.mark.django_db
class TestWidgetDeleteView:
    def test_gm_can_delete_widget(self, client, gm_user):
        widget = HomePageWidget.objects.create(widget_type="rich_text", order=1)
        client.force_login(gm_user)
        response = client.post(f"/homepage/widgets/{widget.pk}/delete/")
        assert response.status_code == 302
        assert not HomePageWidget.objects.filter(pk=widget.pk).exists()

    def test_player_cannot_delete_widget(self, client, player_user):
        widget = HomePageWidget.objects.create(widget_type="rich_text", order=1)
        client.force_login(player_user)
        response = client.post(f"/homepage/widgets/{widget.pk}/delete/")
        assert response.status_code == 403
        assert HomePageWidget.objects.filter(pk=widget.pk).exists()


@pytest.mark.django_db
class TestWidgetMoveView:
    def test_gm_can_move_widget_down(self, client, gm_user):
        w1 = HomePageWidget.objects.create(widget_type="rich_text", order=1)
        w2 = HomePageWidget.objects.create(widget_type="campaign_list", order=2)
        client.force_login(gm_user)
        response = client.post(f"/homepage/widgets/{w1.pk}/move/", {"direction": "down"})
        assert response.status_code == 302
        w1.refresh_from_db()
        w2.refresh_from_db()
        assert w1.order > w2.order

    def test_gm_can_move_widget_up(self, client, gm_user):
        w1 = HomePageWidget.objects.create(widget_type="rich_text", order=1)
        w2 = HomePageWidget.objects.create(widget_type="campaign_list", order=2)
        client.force_login(gm_user)
        response = client.post(f"/homepage/widgets/{w2.pk}/move/", {"direction": "up"})
        assert response.status_code == 302
        w1.refresh_from_db()
        w2.refresh_from_db()
        assert w2.order < w1.order


@pytest.mark.django_db
class TestWidgetVisibilityFilter:
    def _make_widgets(self):
        HomePageWidget.objects.create(widget_type="rich_text", order=1, visibility="public")
        HomePageWidget.objects.create(widget_type="campaign_list", order=2, visibility="player")
        HomePageWidget.objects.create(widget_type="image_banner", order=3, visibility="gm_only")

    def test_anonymous_sees_only_public(self, client):
        self._make_widgets()
        response = client.get("/")
        assert response.status_code == 200
        assert b"campaign_list" not in response.content
        assert b"image_banner" not in response.content

    def test_player_sees_public_and_player(self, client, player_user):
        self._make_widgets()
        client.force_login(player_user)
        response = client.get("/")
        assert response.status_code == 200
        assert b"image_banner" not in response.content

    def test_gm_sees_all_widgets(self, client, gm_user):
        self._make_widgets()
        client.force_login(gm_user)
        response = client.get("/")
        assert response.status_code == 200
