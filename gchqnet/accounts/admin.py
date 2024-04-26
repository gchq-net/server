from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "display_name", "is_superuser")
    list_filter = ("is_superuser", "is_active", "groups")
    search_fields = ("username", "display_name", "email")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("display_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "display_name", "password1", "password2"),
            },
        ),
    )


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.site_title = "GCHQ.NET Admin"
admin.site.site_header = "Great Camp Hexpansion Quest"
admin.site.index_title = "Admin Panel"
