import os
import random

from django.core.management.base import BaseCommand

from gchqnet.accounts.factories import BadgeFactory
from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import BasicAchievementEvent
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.quest.factories import LocationFactory
from gchqnet.quest.models import CaptureEvent, Location, RawCaptureEvent
from gchqnet.quest.models.captures import CaptureLog
from gchqnet.quest.models.scores import ScoreRecord
from gchqnet.quest.repository import update_score_for_user


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
        if not os.environ.get("GCHQ_ENABLE_DATA_GENERATION", "false") == "true":
            self.stdout.write("Data generation is disabled. Please set GCHQ_ENABLE_DATA_GENERATION=true env var.")
            return

        if not input("Please type 1449 as written: ") == "one thousand four hundred and forty nine":
            self.stdout.write("Nope")
            return

        BasicAchievementEvent.objects.all().delete()
        CaptureEvent.objects.all().delete()
        CaptureLog.objects.all().delete()
        RawCaptureEvent.objects.all().delete()
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
                for i in range(random.randint(1, 3)):  # noqa: S311
                    raw_event = RawCaptureEvent.objects.create(
                        badge=badge, hexpansion=location.hexpansion, created_by=badge.user
                    )
                    CaptureLog.objects.create(raw_capture_event=raw_event, location=location, created_by=badge.user)
                    if i == 1:
                        capture_event = CaptureEvent.objects.create(
                            raw_capture_event=raw_event, location=location, created_by=badge.user
                        )
                        ScoreRecord.objects.create(
                            capture_event=capture_event, user=badge.user, score=location.difficulty
                        )

            update_score_for_user(badge.user)

        self.stdout.write("Generated fake data")
