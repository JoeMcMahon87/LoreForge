import pytest

from apps.worlds.models import WorldConfig
from apps.worlds.services import (
    create_campaign,
    get_all_campaigns,
    get_world_config,
    update_world_config,
)


@pytest.mark.django_db
class TestGetWorldConfig:
    def test_returns_singleton(self):
        config = get_world_config()
        assert isinstance(config, WorldConfig)
        assert config.pk == 1

    def test_returns_same_instance_on_repeated_calls(self):
        c1 = get_world_config()
        c2 = get_world_config()
        assert c1.pk == c2.pk


@pytest.mark.django_db
class TestUpdateWorldConfig:
    def test_updates_name(self):
        config = update_world_config(name="Greyhawk")
        config.refresh_from_db()
        assert config.name == "Greyhawk"

    def test_updates_tagline_and_description(self):
        config = update_world_config(name="Eberron", tagline="Welcome", description="A world of magic.")
        config.refresh_from_db()
        assert config.tagline == "Welcome"
        assert config.description == "A world of magic."

    def test_does_not_create_second_row(self):
        update_world_config(name="World A")
        update_world_config(name="World B")
        assert WorldConfig.objects.count() == 1


@pytest.mark.django_db
class TestCreateCampaign:
    def test_creates_campaign(self):
        campaign = create_campaign(name="First Campaign")
        assert campaign.pk is not None
        assert campaign.name == "First Campaign"

    def test_slug_auto_generated(self):
        campaign = create_campaign(name="The Dark Descent")
        assert campaign.slug == "the-dark-descent"

    def test_slug_globally_unique(self):
        c1 = create_campaign(name="Session Zero")
        c2 = create_campaign(name="Session Zero")
        assert c1.slug != c2.slug
        assert c2.slug == "session-zero-2"


@pytest.mark.django_db
class TestGetAllCampaigns:
    def test_returns_all_campaigns_ordered_by_created_at(self):
        create_campaign(name="Alpha")
        create_campaign(name="Beta")
        campaigns = get_all_campaigns()
        assert campaigns.count() == 2
        names = list(campaigns.values_list("name", flat=True))
        assert names == ["Alpha", "Beta"]
