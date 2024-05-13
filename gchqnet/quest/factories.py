import factory
import factory.fuzzy

from gchqnet.hexpansion.factories import HexpansionFactory

from .models import LocationDifficulty


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.Location"

    display_name = factory.Faker("slug")
    description = factory.Faker("paragraph")
    hint = factory.Faker("slug")
    difficulty = factory.fuzzy.FuzzyChoice(LocationDifficulty)
    hexpansion = factory.SubFactory(HexpansionFactory)
