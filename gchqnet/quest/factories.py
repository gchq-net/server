import factory
import factory.fuzzy

from gchqnet.accounts.factories import UserFactory
from gchqnet.hexpansion.factories import HexpansionFactory

from .models import LocationDifficulty


class LocationInstallationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.LocationInstallation"

    hexpansion = factory.SubFactory(HexpansionFactory)
    created_by = factory.SubFactory(UserFactory)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.Location"

    display_name = factory.Faker("slug")
    description = factory.Faker("paragraph")
    difficulty = factory.fuzzy.FuzzyChoice(LocationDifficulty)
    installation = factory.RelatedFactory(LocationInstallationFactory, factory_related_name="location")
