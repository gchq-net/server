from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Field,
    Fieldset,
    Fixed,
    Layout,
    Submit,
)
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User
from .totp import CustomTOTP


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

    def clean_display_name(self) -> str:
        display_name = self.cleaned_data["display_name"].strip()

        # Do a case-insensitive check for other users with the display name as their username
        q = User.objects.filter(username__iexact=display_name)
        if q.exclude(id=self.instance.id):
            raise ValidationError("That name is not available, sorry.")

        return display_name


class CredentialsLoginForm(AuthenticationForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Login"))


class BadgeLoginUsernameForm(forms.Form):
    account_name = forms.CharField(label="Account name", max_length=30, required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Continue"))

    def clean_account_name(self) -> User:
        try:
            return User.objects.get(username=self.cleaned_data["account_name"], is_active=True)
        except User.DoesNotExist as e:
            raise ValidationError("Unable to find your account name. Have you spelled it correctly?") from e


class BadgeLoginChallengeForm(forms.Form):
    security_code = forms.CharField(label="Security Code", min_length=6, max_length=6, required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                Field.text("security_code", field_width=Fixed.FIVE),
            ),
            Submit("submit", "Continue"),
        )

    def clean_security_code(self) -> str:
        security_code = self.cleaned_data["security_code"].strip()
        is_valid = any(
            CustomTOTP(mac_address).verify(security_code, valid_window=1)
            for mac_address in self.user.badges.values_list("mac_address", flat=True)
        )
        if not is_valid:
            raise ValidationError("That isn't the correct code.")
        return security_code
