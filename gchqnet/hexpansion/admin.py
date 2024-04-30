from django.contrib import admin
from django.http import HttpRequest

from .models import Hexpansion


class HexpansionAdmin(admin.ModelAdmin):
    list_display = ("human_identifier", "eeprom_serial_number", "serial_number")
    list_filter = ("hardware_revision", ("installation", admin.EmptyFieldListFilter))
    readonly_fields = (
        "id",
        "installation",
        "eeprom_serial_number",
        "serial_number",
        "created_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("human_identifier", "eeprom_serial_number", "serial_number")
    fieldsets = (
        (None, {"fields": ("human_identifier", "installation")}),
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

    # @admin.display(description="Installation")
    # def installation_info(self, obj: Hexpansion) -> bool:
    #     return obj.installation

    def has_add_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual creation of Hexpansions."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Hexpansion | None = None) -> bool:
        """Disable manual deletion of Hexpansions."""
        return False


admin.site.register(Hexpansion, HexpansionAdmin)
