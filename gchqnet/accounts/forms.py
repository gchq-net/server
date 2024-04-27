from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Submit
from django import forms

from .models import User


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Account name")
    display_name = forms.CharField(max_length=30, help_text="A name or nickname to be displayed on the leaderboard")

    class Meta:
        model = User
        fields = ("username", "display_name")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Update profile"))
