from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Submit,
)
from django.forms import ModelForm

from gchqnet.accounts.models.user import User
from gchqnet.achievements.models import BasicAchievement


class BasicAchievementCreateForm(ModelForm):
    class Meta:
        model = BasicAchievement
        fields = ("display_name", "difficulty", "award_type")

    def __init__(self, *args: Any, user: User, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create"))

    def save(self, commit: bool = True) -> BasicAchievement:  # noqa: FBT001, FBT002
        if not self.instance.pk:
            self.instance.created_by = self.user
        return super().save(commit)
