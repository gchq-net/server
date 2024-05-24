import pytest
from django.urls import reverse

from gchqnet.achievements.models import BasicAchievement
from gchqnet.logistics.tests.test_views import LogisticsAccessTestMixin


@pytest.mark.django_db
class TestAchievementsBasicListView(LogisticsAccessTestMixin):
    url = reverse("achievements:basic_achievements_list")


@pytest.mark.django_db
class TestAchievementsBasicDetailView(LogisticsAccessTestMixin):
    @property
    def url(self) -> str:  # type: ignore[override]
        external_achievement, _ = BasicAchievement.objects.get_or_create(
            display_name="bees",
            difficulty=10,
            award_type="external",
        )
        return reverse("achievements:basic_achievements_detail", args=[external_achievement.id])
