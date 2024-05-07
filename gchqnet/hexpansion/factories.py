import string
from random import randint
from uuid import UUID

import factory
import factory.fuzzy

from gchqnet.accounts.factories import UserFactory


class HexpansionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "hexpansion.Hexpansion"  # Equivalent to ``model = myapp.models.User``

    human_identifier = factory.fuzzy.FuzzyText(length=4, chars=string.ascii_uppercase)
    eeprom_serial_number = factory.fuzzy.FuzzyInteger(low=0, high=(2**15) - 1)
    serial_number = factory.LazyFunction(lambda: UUID(int=randint(0, (2**72) - 1)))  # noqa: S311
    created_by = factory.SubFactory(UserFactory)
