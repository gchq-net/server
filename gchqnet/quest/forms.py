from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Submit,
)
from django import forms

from gchqnet.accounts.models.user import User

from .models import Leaderboard


class LeaderboardUpdateForm(forms.ModelForm):
    display_name = forms.CharField(label="Name", max_length=40, required=True)

    class Meta:
        model = Leaderboard
        fields = ["display_name", "enable_invites"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Update leaderboard"))


class LeaderboardCreateForm(forms.ModelForm):
    display_name = forms.CharField(label="Name", max_length=40, required=True)

    class Meta:
        model = Leaderboard
        fields = ["display_name"]

    def __init__(self, *args: Any, user: User, **kwargs: Any) -> None:
        self.user = user

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create leaderboard"))

    def save(self, commit: bool = True) -> Leaderboard:  # noqa: FBT001, FBT002
        self.instance.owner = self.user
        self.instance.created_by = self.user

        instance = super().save(commit)

        instance.members.add(self.user)
        instance.save()
        return instance


class LeaderboardInviteAcceptDeclineForm(forms.Form):
    def __init__(self, *args: Any, post_url: str, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Accept Invitation", formaction=f"{post_url}?accept=true"))
        self.helper.add_input(
            Submit(
                "submit", "Decline Invitation", css_class="govuk-button--warning", formaction=f"{post_url}?accept=false"
            )
        )
