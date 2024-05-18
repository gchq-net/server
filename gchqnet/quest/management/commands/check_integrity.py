from django.core.management.base import BaseCommand

from gchqnet.accounts.models.user import User
from gchqnet.quest.models import CaptureEvent, ScoreRecord
from gchqnet.quest.repository import update_score_for_user


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
        # Capture Events
        capture_events = CaptureEvent.objects.prefetch_related("location").select_related(
            "raw_capture_event__badge", "score_record"
        )

        for ce in capture_events:
            if ce.raw_capture_event.badge.user_id != ce.created_by_id:
                self.stdout.write(f"Issue found with {ce} created_by")
                ce.created_by_id = ce.raw_capture_event.badge.user_id
                ce.save(update_fields=["created_by_id"])

            try:
                score_record = ce.score_record
            except ScoreRecord.DoesNotExist:
                self.stdout.write(f"Missing score record for {ce}. Fixing.")
                ScoreRecord.objects.create(user=ce.created_by, capture_event=ce, score=ce.location.difficulty)
            else:
                if ce.location.difficulty != score_record.score:
                    self.stdout.write(f"Issue found with {ce} score")
                    score_record.score = ce.location.difficulty
                    score_record.save(update_fields=["score"])

        self.stdout.write(f"Checked {len(capture_events)} capture events")

        for user in User.objects.all():
            update_score_for_user(user)

        self.stdout.write("Bumped scores for users")
