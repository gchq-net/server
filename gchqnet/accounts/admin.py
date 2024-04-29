from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Badge, User


class BadgeAdminForm(ModelForm):
    model = Badge

    def clean_mac_address(self) -> str:
        return self.cleaned_data["mac_address"].upper().replace(":", "-")


class BadgeAdminMixin(admin.options.BaseModelAdmin):
    form = BadgeAdminForm
    readonly_fields = ("id", "created_at", "updated_at")

    def has_delete_permission(self, request: HttpRequest, obj: Badge | None = None) -> bool:
        return False


class BadgeInlineAdmin(BadgeAdminMixin, admin.StackedInline):
    model = Badge
    extra = 0


class BadgeAdmin(BadgeAdminMixin, admin.ModelAdmin):
    model = Badge
    list_display = ("mac_address", "user_display_name", "user_username", "is_enabled")
    list_filter = ("is_enabled",)
    search_fields = ("mac_address", "user__display_name", "user__username")

    @admin.display(ordering="user__display_name", description="User Display Name")
    def user_display_name(self, badge: Badge) -> str:
        return badge.user.display_name

    @admin.display(ordering="user__username", description="Username")
    def user_username(self, badge: Badge) -> str:
        return badge.user.username

    def get_queryset(self, request: HttpRequest) -> QuerySet[Badge]:
        return super().get_queryset(request).select_related("user")


class UserAdmin(DjangoUserAdmin):
    inlines = (BadgeInlineAdmin,)
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
admin.site.register(Badge, BadgeAdmin)
admin.site.unregister(Group)
admin.site.site_title = "GCHQ.NET Admin"
admin.site.site_header = "Great Camp Hexpansion Quest"
admin.site.index_title = "Admin Panel"
