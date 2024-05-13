import random

from django.core.management.base import BaseCommand

from gchqnet.accounts.factories import BadgeFactory
from gchqnet.accounts.models.user import User
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import CaptureEvent, Location, RawCaptureEvent


class Command(BaseCommand):
    help = "Generate fake data"  # noqa: A003

    def handle(
        self,
        *,
        verbosity: int,
        settings: str,
        pythonpath: str,
        traceback: bool,
        no_color: bool,
        force_color: bool,
        skip_checks: bool,
    ) -> None:
        RawCaptureEvent.objects.all().delete()
        CaptureEvent.objects.all().delete()
        Location.objects.all().delete()
        Hexpansion.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        assert User.objects.filter(is_superuser=True).first() is not None

        badges = BadgeFactory.create_batch(size=500)
        locations = LocationFactory.create_batch(
            size=100,
            created_by=User.objects.filter(is_superuser=True).first(),
        )

        for badge in badges:
            sample = random.sample(locations, k=random.randint(0, len(locations)))  # noqa: S311
            for location in sample:
                raw_event = RawCaptureEvent.objects.create(
                    badge=badge, hexpansion=location.hexpansion, created_by=badge.user
                )
                CaptureEvent.objects.create(raw_capture_event=raw_event, location=location, created_by=badge.user)

        self.stdout.write("Generated fake data")
