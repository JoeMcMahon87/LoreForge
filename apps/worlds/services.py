from django.db import transaction
from django.db.models import Q, QuerySet

from apps.worlds.models import Campaign, World, WorldMembership


def create_world(owner, name: str, description: str = "") -> World:
    """Create a world and automatically add owner as GM member (atomic)."""
    with transaction.atomic():
        world = World.objects.create(owner=owner, name=name, description=description)
        WorldMembership.objects.create(
            user=owner, world=world, role=WorldMembership.Role.GM
        )
    return world


def get_worlds_for_user(user) -> QuerySet:
    """Worlds where user is owner OR has a WorldMembership."""
    return World.objects.filter(
        Q(owner=user) | Q(memberships__user=user)
    ).distinct()


def add_member(world: World, user, role: str) -> WorldMembership:
    """Add user to world. Raises ValueError if already a member."""
    if WorldMembership.objects.filter(world=world, user=user).exists():
        raise ValueError(f"{user} is already a member of {world}.")
    return WorldMembership.objects.create(user=user, world=world, role=role)


def remove_member(world: World, user) -> None:
    """Remove user's WorldMembership. Raises ValueError if user is the owner."""
    if world.owner == user:
        raise ValueError("Cannot remove the world owner from membership.")
    WorldMembership.objects.filter(world=world, user=user).delete()


def get_campaigns_for_world(world: World) -> QuerySet:
    """Return campaigns for a world ordered by created_at."""
    return world.campaigns.order_by("created_at")


def create_campaign(world: World, name: str, description: str = "") -> Campaign:
    """Create a campaign scoped to the given world."""
    return Campaign.objects.create(world=world, name=name, description=description)
