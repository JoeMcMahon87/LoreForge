import pytest

from apps.worlds.models import Campaign, WorldConfig


@pytest.mark.django_db
class TestWorldConfig:
    def test_get_solo_creates_singleton(self):
        config = WorldConfig.get_solo()
        assert config.pk == 1

    def test_get_solo_does_not_create_second_row(self):
        WorldConfig.get_solo()
        WorldConfig.get_solo()
        assert WorldConfig.objects.count() == 1

    def test_str_returns_name(self):
        config = WorldConfig.get_solo()
        config.name = "Faerun"
        config.save()
        assert str(config) == "Faerun"

    def test_default_name(self):
        config = WorldConfig.get_solo()
        assert config.name == "My World"

    def test_default_theme_color(self):
        config = WorldConfig.get_solo()
        assert config.theme_color == "#4f46e5"


@pytest.mark.django_db
class TestCampaignModel:
    def test_str_returns_name(self):
        campaign = Campaign.objects.create(name="Session Zero")
        assert str(campaign) == "Session Zero"

    def test_slug_auto_generated_from_name(self):
        campaign = Campaign.objects.create(name="The First Quest")
        assert campaign.slug == "the-first-quest"

    def test_default_status_is_active(self):
        campaign = Campaign.objects.create(name="My Campaign")
        assert campaign.status == Campaign.Status.ACTIVE

    def test_slug_globally_unique_gets_suffix(self):
        c1 = Campaign.objects.create(name="Session Zero")
        c2 = Campaign.objects.create(name="Session Zero")
        assert c1.slug == "session-zero"
        assert c2.slug == "session-zero-2"

    def test_slug_stable_on_rename(self):
        campaign = Campaign.objects.create(name="Original Name")
        original_slug = campaign.slug
        campaign.name = "New Name"
        campaign.save()
        assert campaign.slug == original_slug
