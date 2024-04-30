from django.contrib import admin
from django.forms import BaseFormSet, ModelForm
from django.http import HttpRequest

from .models import Coordinates, Location, LocationInstallation


class CoordinatesAdmin(admin.StackedInline):
    model = Coordinates
    fields = ("lat", "long", "id", "created_at", "created_by", "updated_at")
    readonly_fields = ("id", "created_at", "created_by", "updated_at")


class LocationInstallationAdmin(admin.StackedInline):
    model = LocationInstallation
    autocomplete_fields = ("hexpansion",)
    fields = ("hexpansion", "created_at", "created_by", "updated_at")
    readonly_fields = ("id", "created_at", "created_by", "updated_at")
    extra = 0


class LocationAdmin(admin.ModelAdmin):
    model = Location
    inlines = (CoordinatesAdmin, LocationInstallationAdmin)
    exclude = ("created_by",)
    list_display = ("display_name", "internal_name", "difficulty", "coordinates")
    list_filter = ("difficulty", ("installation", admin.EmptyFieldListFilter))
    readonly_fields = ("id", "created_at", "created_by", "updated_at")
    search_fields = ("display_name", "internal_name")
    fieldsets = (
        (None, {"fields": ("display_name", "difficulty")}),
        (
            "Internal Info",
            {
                "description": "Please provide plenty of detail to help others install, maintain and remove locations. This information will not be public.",  # noqa: E501
                "fields": ("internal_name", "description"),
            },
        ),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    def save_form(self, request: HttpRequest, form: ModelForm, change: bool) -> Location:  # noqa: FBT001
        instance = super().save_form(request, form, change)
        instance.created_by = request.user
        return instance

    def save_formset(self, request: HttpRequest, form: ModelForm, formset: BaseFormSet, change: bool) -> None:  # noqa: FBT001
        instances = formset.save(commit=False)  # type: ignore[attr-defined]
        for obj in instances:
            if obj.id:
                obj.created_by = request.user
        formset.save()  # type: ignore[attr-defined]

    def has_delete_permission(self, request: HttpRequest, obj: Location | None = None) -> bool:
        """Disable manual deletion of locations."""
        return False


admin.site.register(Location, LocationAdmin)
