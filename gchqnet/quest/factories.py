import factory
import factory.fuzzy

from gchqnet.accounts.factories import UserFactory
from gchqnet.hexpansion.factories import HexpansionFactory

from .models import LocationDifficulty


class CoordinatesFactory(factory.django.DjangoModelFactory):
    lat = factory.fuzzy.FuzzyFloat(52.03887, 52.04396)
    long = factory.fuzzy.FuzzyFloat(-2.38255, -2.37431)

    class Meta:
        model = "quest.Coordinates"


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.Location"

    display_name = factory.Faker("slug")
    description = factory.Faker("paragraph")
    hint = factory.Faker("slug")
    difficulty = factory.fuzzy.FuzzyChoice(LocationDifficulty)
    hexpansion = factory.SubFactory(HexpansionFactory)
    coordinates = factory.RelatedFactory(
        CoordinatesFactory, factory_related_name="location", created_by=factory.SelfAttribute("location.created_by")
    )

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None) -> None:  # type: ignore  # noqa
        """Save again the instance if creating and at least one hook ran."""
        if create and results:
            instance.save()


class LeaderboardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.Leaderboard"

    display_name = factory.Faker("slug")
    owner = factory.SubFactory(UserFactory)
    created_by = factory.SelfAttribute("owner")
