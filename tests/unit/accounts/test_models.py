import pytest

from apps.accounts.models import CustomUser


@pytest.mark.django_db
def test_is_gm_returns_true_for_gm_role(gm_user):
    assert gm_user.is_gm() is True


@pytest.mark.django_db
def test_is_gm_returns_false_for_player_role(player_user):
    assert player_user.is_gm() is False


@pytest.mark.django_db
def test_is_admin_user_returns_true_for_admin_role(db):
    user = CustomUser.objects.create_user(username="testadmin", password="pass1234!", role="admin")
    assert user.is_admin_user() is True


@pytest.mark.django_db
def test_is_admin_user_returns_false_for_gm_role(gm_user):
    assert gm_user.is_admin_user() is False


@pytest.mark.django_db
def test_default_role_is_player(db):
    user = CustomUser.objects.create_user(username="defaultuser", password="pass1234!")
    assert user.role == CustomUser.Role.PLAYER
