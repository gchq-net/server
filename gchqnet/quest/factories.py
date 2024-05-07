import factory
import factory.fuzzy

from .models import LocationDifficulty


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "quest.Location"

    display_name = factory.Faker("slug")
    description = factory.Faker("paragraph")
    difficulty = factory.fuzzy.FuzzyChoice(LocationDifficulty)
