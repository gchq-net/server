import factory
import factory.fuzzy

from gchqnet.accounts.usernames import generate_username


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.User"

    username = factory.LazyFunction(generate_username)
    display_name = factory.LazyAttribute(lambda o: o.username)


class BadgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.Badge"

    mac_address = factory.Faker("hexify", text="^^-^^-^^-^^-^^-^^", upper=True)
    user = factory.SubFactory(UserFactory)
