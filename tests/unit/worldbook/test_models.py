from apps.worldbook.models import Faction, Item, Location, Lore, Tag


class TestTag:
    def test_str_returns_name(self, db):
        tag = Tag.objects.create(name="Arcane")
        assert str(tag) == "Arcane"

    def test_slug_auto_generated_from_name(self, db):
        tag = Tag.objects.create(name="Dragon Lore")
        assert tag.slug == "dragon-lore"

    def test_slug_collision_gets_suffix(self, db):
        Tag.objects.create(name="Dragon")
        tag2 = Tag.objects.create(name="Dragon!")  # same slug "dragon", different name
        assert tag2.slug == "dragon-2"


class TestLocation:
    def test_str_returns_title(self, db, gm_user):
        loc = Location.objects.create(title="Dragon Peak", created_by=gm_user)
        assert str(loc) == "Dragon Peak"

    def test_slug_auto_generated_from_title(self, db, gm_user):
        loc = Location.objects.create(title="Dark Forest", created_by=gm_user)
        assert loc.slug == "dark-forest"

    def test_slug_stable_on_rename(self, db, gm_user):
        loc = Location.objects.create(title="Old Keep", created_by=gm_user)
        original_slug = loc.slug
        loc.title = "New Keep Name"
        loc.save()
        assert loc.slug == original_slug

    def test_slug_collision_gets_suffix(self, db, gm_user):
        Location.objects.create(title="Dragon Peak", created_by=gm_user)
        loc2 = Location.objects.create(title="Dragon Peak", created_by=gm_user)
        assert loc2.slug == "dragon-peak-2"

    def test_default_visibility_is_gm_only(self, db, gm_user):
        loc = Location.objects.create(title="Secret Place", created_by=gm_user)
        assert loc.visibility == "gm_only"


class TestFaction:
    def test_str_returns_title(self, db, gm_user):
        faction = Faction.objects.create(title="The Thieves Guild", created_by=gm_user)
        assert str(faction) == "The Thieves Guild"

    def test_default_visibility_is_gm_only(self, db, gm_user):
        faction = Faction.objects.create(title="Shadow Council", created_by=gm_user)
        assert faction.visibility == "gm_only"


class TestItem:
    def test_str_returns_title(self, db, gm_user):
        item = Item.objects.create(title="Vorpal Sword", created_by=gm_user)
        assert str(item) == "Vorpal Sword"

    def test_rarity_defaults_to_common(self, db, gm_user):
        item = Item.objects.create(title="Plain Dagger", created_by=gm_user)
        assert item.rarity == "common"

    def test_default_visibility_is_gm_only(self, db, gm_user):
        item = Item.objects.create(title="Hidden Relic", created_by=gm_user)
        assert item.visibility == "gm_only"


class TestLore:
    def test_str_returns_title(self, db, gm_user):
        lore = Lore.objects.create(title="The First Age", created_by=gm_user)
        assert str(lore) == "The First Age"

    def test_lore_type_defaults_to_other(self, db, gm_user):
        lore = Lore.objects.create(title="Unknown Tales", created_by=gm_user)
        assert lore.lore_type == "other"

    def test_default_visibility_is_gm_only(self, db, gm_user):
        lore = Lore.objects.create(title="Secret History", created_by=gm_user)
        assert lore.visibility == "gm_only"
