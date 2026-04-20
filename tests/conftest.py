import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def gm_user(db):
    from apps.accounts.models import CustomUser

    return CustomUser.objects.create_user(username="testgm", password="pass1234!", role="gm")


@pytest.fixture
def player_user(db):
    from apps.accounts.models import CustomUser

    return CustomUser.objects.create_user(username="testplayer", password="pass1234!", role="player")


@pytest.fixture
def world(db, gm_user):
    from apps.worlds.services import create_world

    return create_world(owner=gm_user, name="Test World")


@pytest.fixture
def campaign(db, world):
    from apps.worlds.services import create_campaign

    return create_campaign(world=world, name="Test Campaign")


@pytest.fixture
def player_member(db, world, player_user):
    from apps.worlds.services import add_member

    return add_member(world=world, user=player_user, role="player")
