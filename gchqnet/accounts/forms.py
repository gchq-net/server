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
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User
from .totp import CustomTOTP


def verify_security_code(user: User, code: str) -> bool:
    return any(
        CustomTOTP(mac_address).verify(code, valid_window=1)
        for mac_address in user.badges.values_list("mac_address", flat=True)
    )


class BaseProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Account name")
    display_name = forms.CharField(
        max_length=30, help_text="A name or nickname to be displayed on the leaderboard"
    )

    auth_success = False
    auth_error_msg = "You must authenticate first"
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "display_name",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")

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

    def clean_new_password2(self) -> None:
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if not password2 or self.errors:
            return None
        if not self.auth_success:
            raise ValidationError(self.auth_error_msg)
        if password1 != password2:
            raise ValidationError("The new passwords do not match.")
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit: bool = True) -> User:  # noqa: FBT001, FBT002
        if self.cleaned_data["new_password2"]:
            self.user.set_password(self.cleaned_data["new_password2"])
        if commit:
            self.user.save()
        return super().save(commit=commit)


class PasswordProfileUpdateForm(BaseProfileUpdateForm):
    current_password = forms.CharField(
        label="Current password", widget=forms.PasswordInput, required=False
    )
    auth_error_msg = "That password is incorrect"

    field_order = [
        "username",
        "display_name",
        "current_password",
        "new_password1",
        "new_password2",
    ]

    def clean_current_password(self) -> str:
        current_password = self.cleaned_data["current_password"]
        if (
            self.user.has_usable_password()
            and current_password
            and not self.user.check_password(current_password)
        ):
            raise ValidationError("That password is incorrect.")
        self.auth_success = True
        return current_password


class TOTPProfileUpdateForm(BaseProfileUpdateForm):
    security_code = forms.CharField(
        label="Badge Security Code", min_length=6, max_length=6, required=False
    )
    auth_error_msg = "That isn't the correct code"

    field_order = [
        "username",
        "display_name",
        "security_code",
        "new_password1",
        "new_password2",
    ]

    def clean_security_code(self) -> str:
        security_code = self.cleaned_data["security_code"].strip()
        if not verify_security_code(self.user, security_code):
            raise ValidationError("That isn't the correct code.")
        self.auth_success = True
        return security_code


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
            return User.objects.get(
                username=self.cleaned_data["account_name"], is_active=True
            )
        except User.DoesNotExist as e:
            raise ValidationError(
                "Unable to find your account name. Have you spelled it correctly?"
            ) from e


class BadgeLoginChallengeForm(forms.Form):
    security_code = forms.CharField(
        label="Security Code", min_length=6, max_length=6, required=True
    )

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
        if not verify_security_code(self.user, security_code):
            raise ValidationError("That isn't the correct code.")
        return security_code
