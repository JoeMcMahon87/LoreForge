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
