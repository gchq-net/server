from django.core.management.base import BaseCommand
from sentry_sdk.crons import monitor

from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import (
    BasicAchievementEvent,
    FirstToCaptureAchievementEvent,
    LocationGroupAchievementEvent,
)
from gchqnet.quest.models import CaptureEvent, ScoreRecord
from gchqnet.quest.repository import update_score_for_user


class Command(BaseCommand):
    help = "Check data integrity"  # noqa: A003

    @monitor(monitor_slug="check-integrity")
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

        for bae in BasicAchievementEvent.objects.all():
            try:
                score_record = bae.score_record
            except ScoreRecord.DoesNotExist:
                self.stdout.write(f"Missing score record for {bae}. Fixing.")
                ScoreRecord.objects.create(
                    user=ce.created_by, basic_achievement_event=bae, score=bae.basic_achievement.difficulty
                )
            else:
                if bae.basic_achievement.difficulty != score_record.score:
                    self.stdout.write(f"Issue found with {bae} score")
                    score_record.score = bae.basic_achievement.difficulty
                    score_record.save(update_fields=["score"])

        for fcae in FirstToCaptureAchievementEvent.objects.all():
            try:
                score_record = fcae.score_record
            except ScoreRecord.DoesNotExist:
                self.stdout.write(f"Missing score record for {fcae}. Fixing.")
                ScoreRecord.objects.create(user=ce.created_by, first_capture_event=fcae, score=fcae.location.difficulty)
            else:
                if fcae.location.difficulty != score_record.score:
                    self.stdout.write(f"Issue found with {fcae} score")
                    score_record.score = fcae.location.difficulty
                    score_record.save(update_fields=["score"])

        for lgae in LocationGroupAchievementEvent.objects.all():
            try:
                score_record = lgae.score_record
            except ScoreRecord.DoesNotExist:
                self.stdout.write(f"Missing score record for {lgae}. Fixing.")
                ScoreRecord.objects.create(
                    user=ce.created_by,
                    location_group_achievement_event=lgae,
                    score=lgae.location_group.difficulty,
                )
            else:
                if lgae.location_group.difficulty != score_record.score:
                    self.stdout.write(f"Issue found with {lgae} score")
                    score_record.score = lgae.location_group.difficulty
                    score_record.save(update_fields=["score"])

        for user in User.objects.all():
            update_score_for_user(user)

        self.stdout.write("Bumped scores for users")
