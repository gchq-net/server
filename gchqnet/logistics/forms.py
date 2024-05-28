from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Submit,
)
from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import Form, ModelForm

from gchqnet.accounts.models.user import User
from gchqnet.hexpansion.models import Hexpansion
from gchqnet.logistics.models import PlannedLocation


class PlannedLocationCreateForm(ModelForm):
    class Meta:
        model = PlannedLocation
        fields = ("internal_name",)

    def __init__(self, *args: Any, user: User, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Create"))

    def save(self, commit: bool = True) -> PlannedLocation:  # noqa: FBT001,FBT002
        if not self.instance.pk:
            self.instance.created_by = self.user
        return super().save(commit)


class PlannedLocationEditForm(ModelForm):
    class Meta:
        model = PlannedLocation
        fields = ("display_name", "hint", "internal_name", "difficulty", "description", "lat", "long")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Save"))


class PlannedLocationDeployForm(forms.Form):
    checked_location = forms.BooleanField(label="I have checked the location on the map above.")
    image = forms.ImageField(label="Please take a photo")
    hexpansion = forms.ModelChoiceField(Hexpansion.objects.filter(location__isnull=True))
    lat = forms.DecimalField(
        label="Latitude",
        max_digits=16,
        decimal_places=13,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        widget=forms.HiddenInput(),
    )
    long = forms.DecimalField(
        label="Longitude",
        max_digits=16,
        decimal_places=13,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Deploy"))


class PlannedLocationDeleteForm(Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Confirm Delete", css_class="govuk-button--warning"))
