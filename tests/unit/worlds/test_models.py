import pytest

from apps.accounts.models import CustomUser
from apps.worlds.models import Campaign, World, WorldMembership


@pytest.fixture
def owner(db):
    return CustomUser.objects.create_user(username="owner", password="pass1234!", role="gm")


@pytest.mark.django_db
class TestWorldModel:
    def test_str_returns_name(self, owner):
        world = World.objects.create(owner=owner, name="Forgotten Realms")
        assert str(world) == "Forgotten Realms"

    def test_slug_auto_generated_from_name(self, owner):
        world = World.objects.create(owner=owner, name="The Lost Kingdom")
        assert world.slug == "the-lost-kingdom"

    def test_slug_collision_gets_suffix(self, owner):
        w1 = World.objects.create(owner=owner, name="My World")
        w2 = World.objects.create(owner=owner, name="My World")
        assert w1.slug == "my-world"
        assert w2.slug == "my-world-2"


@pytest.mark.django_db
class TestCampaignModel:
    def test_str_returns_name(self, owner):
        world = World.objects.create(owner=owner, name="Eberron")
        campaign = Campaign.objects.create(world=world, name="Session Zero")
        assert str(campaign) == "Session Zero"

    def test_slug_auto_generated_from_name(self, owner):
        world = World.objects.create(owner=owner, name="Eberron")
        campaign = Campaign.objects.create(world=world, name="The First Quest")
        assert campaign.slug == "the-first-quest"

    def test_default_status_is_active(self, owner):
        world = World.objects.create(owner=owner, name="Eberron")
        campaign = Campaign.objects.create(world=world, name="My Campaign")
        assert campaign.status == Campaign.Status.ACTIVE

    def test_slug_collision_scoped_to_world(self, owner):
        w1 = World.objects.create(owner=owner, name="World One")
        w2 = World.objects.create(owner=owner, name="World Two")
        c1 = Campaign.objects.create(world=w1, name="Session Zero")
        c2 = Campaign.objects.create(world=w2, name="Session Zero")
        # Two different worlds can share the same campaign slug
        assert c1.slug == "session-zero"
        assert c2.slug == "session-zero"

    def test_slug_collision_within_world_gets_suffix(self, owner):
        world = World.objects.create(owner=owner, name="Greyhawk")
        c1 = Campaign.objects.create(world=world, name="Session Zero")
        c2 = Campaign.objects.create(world=world, name="Session Zero")
        assert c1.slug == "session-zero"
        assert c2.slug == "session-zero-2"


@pytest.mark.django_db
class TestWorldMembership:
    def test_unique_together_prevents_duplicate_membership(self, owner):
        from django.db import IntegrityError

        world = World.objects.create(owner=owner, name="Faerun")
        WorldMembership.objects.create(user=owner, world=world, role="gm")
        with pytest.raises(IntegrityError):
            WorldMembership.objects.create(user=owner, world=world, role="player")
