from typing import Any

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import (
    Submit,
)
from django.forms import ModelForm

from gchqnet.accounts.models.user import User
from gchqnet.logistics.models import PlannedLocation


class PlannedLocationCreateForm(ModelForm):
    class Meta:
        model = PlannedLocation
        fields = ("display_name", "hint", "internal_name", "description")

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
        fields = ("display_name", "hint", "internal_name", "description", "lat", "long")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Save"))
