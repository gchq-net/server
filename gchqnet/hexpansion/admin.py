from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Hexpansion


class HexpansionAdmin(admin.ModelAdmin):
    list_display = ("human_identifier", "eeprom_serial_number", "serial_number")
    list_filter = ("hardware_revision", ("installation", admin.EmptyFieldListFilter))
    readonly_fields = (
        "id",
        "installation_info",
        "eeprom_serial_number",
        "serial_number",
        "created_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("human_identifier", "eeprom_serial_number", "serial_number")
    fieldsets = (
        (None, {"fields": ("human_identifier", "installation_info")}),
        (
            ("Hardware Info"),
            {
                "fields": (
                    "hardware_revision",
                    "serial_number",
                    "eeprom_serial_number",
                ),
            },
        ),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    @admin.display(description="Installed at")
    def installation_info(self, obj: Hexpansion) -> str | None:
        if location := obj.installation.location:
            url = reverse("admin:quest_location_change", args=[location.id])
            return mark_safe(f'<a href="{url}">{location}</a>')  # noqa: S308
        return None

    def has_add_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual creation of Hexpansions."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual deletion of Hexpansions."""
        return False


admin.site.register(Hexpansion, HexpansionAdmin)
