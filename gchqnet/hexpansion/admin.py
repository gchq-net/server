from django.contrib import admin
from django.http import HttpRequest

from .models import Hexpansion


class HexpansionAdmin(admin.ModelAdmin):
    list_display = ("human_identifier", "eeprom_serial_number", "serial_number")
    list_filter = ("hardware_revision",)
    readonly_fields = ("id", "eeprom_serial_number", "serial_number", "created_by", "created_at", "updated_at")
    search_fields = ("human_identifier", "eeprom_serial_number", "serial_number")
    fieldsets = (
        (None, {"fields": ("human_identifier",)}),
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
        ("Database Info", {"fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    def has_add_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual creation of Hexpansions."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual deletion of Hexpansions."""
        return False


admin.site.register(Hexpansion, HexpansionAdmin)
