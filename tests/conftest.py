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
def world_config(db):
    from apps.worlds.models import WorldConfig

    return WorldConfig.get_solo()


@pytest.fixture
def campaign(db):
    from apps.worlds.services import create_campaign

    return create_campaign(name="Test Campaign")


@pytest.fixture
def location(db, gm_user):
    from apps.worldbook.services import create_location

    return create_location(title="Dragon Peak", content="A tall mountain.", visibility="gm_only", created_by=gm_user)


@pytest.fixture
def faction(db, gm_user):
    from apps.worldbook.services import create_faction

    return create_faction(title="The Guild", content="A merchant guild.", visibility="gm_only", created_by=gm_user)


@pytest.fixture
def item(db, gm_user):
    from apps.worldbook.services import create_item

    return create_item(title="Magic Sword", content="A sharp blade.", visibility="gm_only", created_by=gm_user)


@pytest.fixture
def lore(db, gm_user):
    from apps.worldbook.services import create_lore

    return create_lore(title="The Old War", content="Ancient history.", visibility="gm_only", created_by=gm_user)
