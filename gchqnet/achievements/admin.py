from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest

from .models import LocationGroup


class LocationGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ("locations",)
    list_display = ("display_name",)
    search_fields = ("display_name",)
    readonly_fields = ("id", "created_at", "created_by", "updated_at")
    fieldsets = (
        (None, {"fields": ("display_name", "difficulty", "locations")}),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    def has_delete_permission(self, request: HttpRequest, obj: LocationGroup | None = None) -> bool:
        return False

    def save_form(self, request: HttpRequest, form: ModelForm, change: bool) -> LocationGroup:  # noqa: FBT001
        created = form.instance.created_at is None
        instance = super().save_form(request, form, change)
        if created:
            instance.created_by = request.user
        return instance


admin.site.register(LocationGroup, LocationGroupAdmin)
