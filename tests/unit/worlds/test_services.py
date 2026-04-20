import pytest

from apps.accounts.models import CustomUser
from apps.worlds.models import WorldMembership
from apps.worlds.services import (
    add_member,
    create_campaign,
    create_world,
    get_worlds_for_user,
    remove_member,
)


@pytest.fixture
def gm(db):
    return CustomUser.objects.create_user(username="gm1", password="pass1234!", role="gm")


@pytest.fixture
def player(db):
    return CustomUser.objects.create_user(username="player1", password="pass1234!", role="player")


@pytest.fixture
def other_user(db):
    return CustomUser.objects.create_user(username="other", password="pass1234!", role="player")


@pytest.mark.django_db
class TestCreateWorld:
    def test_creates_world_and_gm_membership_atomically(self, gm):
        world = create_world(owner=gm, name="Mystraven")
        assert world.pk is not None
        assert WorldMembership.objects.filter(
            user=gm, world=world, role=WorldMembership.Role.GM
        ).exists()

    def test_create_world_sets_owner(self, gm):
        world = create_world(owner=gm, name="Mystraven")
        assert world.owner == gm


@pytest.mark.django_db
class TestGetWorldsForUser:
    def test_returns_owned_worlds(self, gm):
        world = create_world(owner=gm, name="My World")
        worlds = get_worlds_for_user(gm)
        assert world in worlds

    def test_returns_member_worlds(self, gm, player):
        world = create_world(owner=gm, name="My World")
        add_member(world=world, user=player, role="player")
        worlds = get_worlds_for_user(player)
        assert world in worlds

    def test_excludes_non_member_worlds(self, gm, other_user):
        create_world(owner=gm, name="My World")
        worlds = get_worlds_for_user(other_user)
        assert worlds.count() == 0

    def test_no_duplicates_when_owner_and_member(self, gm):
        create_world(owner=gm, name="My World")
        worlds = get_worlds_for_user(gm)
        assert worlds.count() == 1


@pytest.mark.django_db
class TestAddMember:
    def test_creates_membership(self, gm, player):
        world = create_world(owner=gm, name="My World")
        membership = add_member(world=world, user=player, role="player")
        assert membership.pk is not None
        assert membership.role == "player"

    def test_raises_if_already_member(self, gm, player):
        world = create_world(owner=gm, name="My World")
        add_member(world=world, user=player, role="player")
        with pytest.raises(ValueError):
            add_member(world=world, user=player, role="player")


@pytest.mark.django_db
class TestRemoveMember:
    def test_removes_membership(self, gm, player):
        world = create_world(owner=gm, name="My World")
        add_member(world=world, user=player, role="player")
        remove_member(world=world, user=player)
        assert not WorldMembership.objects.filter(user=player, world=world).exists()

    def test_raises_if_removing_owner(self, gm):
        world = create_world(owner=gm, name="My World")
        with pytest.raises(ValueError):
            remove_member(world=world, user=gm)


@pytest.mark.django_db
class TestCreateCampaign:
    def test_associates_campaign_with_world(self, gm):
        world = create_world(owner=gm, name="My World")
        campaign = create_campaign(world=world, name="First Campaign")
        assert campaign.world == world
        assert campaign.pk is not None
