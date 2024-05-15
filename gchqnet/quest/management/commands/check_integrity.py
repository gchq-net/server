from django.core.management.base import BaseCommand

from gchqnet.achievements.models import BasicAchievementEvent
from gchqnet.quest.models import CaptureEvent


class Command(BaseCommand):
    help = "Check data integrity"  # noqa: A003

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
        capture_events = CaptureEvent.objects.prefetch_related("location").select_related("raw_capture_event__badge")

        for ce in capture_events:
            if ce.location.difficulty != ce.score:
                self.stdout.write(f"Issue found with {ce} score")

            if ce.raw_capture_event.badge.user_id != ce.created_by_id:
                self.stdout.write(f"Issue found with {ce} created_by")

        self.stdout.write(f"Checked {len(capture_events)} capture events")

        basic_achievement_events = BasicAchievementEvent.objects.prefetch_related("achievement")
        for bae in basic_achievement_events:
            if bae.achievement.difficulty != bae.score:
                self.stdout.write(f"Issue found with {bae} score")

        self.stdout.write(f"Checked {len(basic_achievement_events)} basic achievement events")
