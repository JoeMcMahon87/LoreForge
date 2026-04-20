import pytest

from apps.home.models import SiteConfig


@pytest.mark.django_db
class TestSiteConfig:
    def test_get_solo_creates_with_defaults(self):
        config = SiteConfig.get_solo()
        assert config.pk == 1
        assert config.site_name == "LoreForge"
        assert "organised" in config.hero_title

    def test_get_solo_returns_same_record(self):
        first = SiteConfig.get_solo()
        second = SiteConfig.get_solo()
        assert first.pk == second.pk
        assert SiteConfig.objects.count() == 1

    def test_str_returns_label(self):
        config = SiteConfig.get_solo()
        assert str(config) == "Site Configuration"
