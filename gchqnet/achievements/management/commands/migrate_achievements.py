from django.core.management.base import BaseCommand

from gchqnet.achievements.constants import BUILTIN_BASIC_ACHIEVEMENTS
from gchqnet.achievements.models import BasicAchievement


class Command(BaseCommand):
    help = "Update builtin achievements in db"  # noqa: A003

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
        for aid, builtin_achievement in BUILTIN_BASIC_ACHIEVEMENTS.items():
            difficulty, display_name, award_type = builtin_achievement
            BasicAchievement.objects.update_or_create(
                id=aid,
                defaults={
                    "display_name": display_name,
                    "difficulty": difficulty,
                    "award_type": award_type,
                },
            )
