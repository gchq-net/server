from django.contrib import admin
from django.forms import BaseFormSet, ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from gchqnet.quest.models.captures import CaptureLog

from .models import CaptureEvent, Coordinates, Leaderboard, Location, RawCaptureEvent


class CoordinatesAdmin(admin.StackedInline):
    model = Coordinates
    fields = ("lat", "long", "id", "created_at", "created_by", "updated_at")
    readonly_fields = ("id", "created_at", "created_by", "updated_at")


class LocationAdmin(admin.ModelAdmin):
    model = Location
    inlines = (CoordinatesAdmin,)
    exclude = ("created_by",)
    list_display = ("display_name", "internal_name", "difficulty", "coordinates")
    list_filter = ("difficulty",)
    readonly_fields = ("id", "created_at", "created_by", "updated_at")
    autocomplete_fields = ("hexpansion",)
    search_fields = ("display_name", "internal_name")
    fieldsets = (
        (None, {"fields": ("display_name", "difficulty", "hint")}),
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
        created = form.instance is None
        instance = super().save_form(request, form, change)
        if created:
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


class ViewOnlyMixin:
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: RawCaptureEvent | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: RawCaptureEvent | None = None) -> bool:
        return False


class RawCaptureEventAdmin(ViewOnlyMixin, admin.ModelAdmin):
    model = RawCaptureEvent

    list_display = ("badge", "hexpansion", "created_at", "created_by")
    fieldsets = (
        (None, {"fields": ("badge", "hexpansion")}),
        (
            "Submission Data",
            {"fields": ("rand", "hmac", "app_rev", "fw_rev")},
        ),
        ("Capture Event", {"fields": ("capture_event", "capture_log")}),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    @admin.display(description="Associated Capture Event")
    def capture_event(self, obj: RawCaptureEvent) -> str | None:
        try:
            capture_event = obj.capture_event
            url = reverse("admin:quest_captureevent_change", args=[capture_event.id])
            return mark_safe(f'<a href="{url}">{capture_event}</a>')  # noqa: S308
        except CaptureEvent.DoesNotExist:
            return "-"

    @admin.display(description="Associated Capture Log")
    def capture_log(self, obj: RawCaptureEvent) -> str | None:
        try:
            capture_log = obj.capture_log
            url = reverse("admin:quest_capturelog_change", args=[capture_log.id])
            return mark_safe(f'<a href="{url}">{capture_log}</a>')  # noqa: S308
        except CaptureLog.DoesNotExist:
            return "-"


class CaptureEventAdmin(ViewOnlyMixin, admin.ModelAdmin):
    model = CaptureEvent

    list_display = ("location", "capture_log", "created_by", "created_at")
    fieldsets = (
        (None, {"fields": ("location", "capture_log")}),
        (
            "Raw Capture Event",
            {
                "fields": (
                    "capturing_user",
                    "badge",
                    "hexpansion",
                    "raw_capture_event",
                )
            },
        ),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    @admin.display(description="Capture Log")
    def capture_log(self, obj: CaptureEvent) -> str:
        try:
            capture_log = obj.raw_capture_event.capture_log
            url = reverse("admin:quest_capturelog_change", args=[capture_log.id])
            return mark_safe(f'<a href="{url}">{capture_log}</a>')  # noqa: S308
        except CaptureLog.DoesNotExist:
            return "-"

    @admin.display(description="User")
    def capturing_user(self, obj: CaptureEvent) -> str:
        user = obj.raw_capture_event.badge.user
        url = reverse("admin:accounts_user_change", args=[user.id])
        return mark_safe(f'<a href="{url}">{user}</a>')  # noqa: S308

    @admin.display(description="Badge")
    def badge(self, obj: CaptureEvent) -> str:
        badge = obj.raw_capture_event.badge
        url = reverse("admin:accounts_badge_change", args=[badge.id])
        return mark_safe(f'<a href="{url}">{badge}</a>')  # noqa: S308

    @admin.display(description="Hexpansion")
    def hexpansion(self, obj: CaptureEvent) -> str:
        hexpansion = obj.raw_capture_event.hexpansion
        url = reverse("admin:hexpansion_hexpansion_change", args=[hexpansion.id])
        return mark_safe(f'<a href="{url}">{hexpansion}</a>')  # noqa: S308


class CaptureLogAdmin(ViewOnlyMixin, admin.ModelAdmin):
    model = CaptureLog

    list_display = ("location", "capture_event", "created_by", "created_at")
    fieldsets = (
        (None, {"fields": ("location", "capture_event")}),
        (
            "Raw Capture Event",
            {
                "fields": (
                    "capturing_user",
                    "badge",
                    "hexpansion",
                    "raw_capture_event",
                )
            },
        ),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    @admin.display(description="Capture Event")
    def capture_event(self, obj: CaptureLog) -> str:
        try:
            capture_event = obj.raw_capture_event.capture_event
            url = reverse("admin:quest_captureevent_change", args=[capture_event.id])
            return mark_safe(f'<a href="{url}">{capture_event}</a>')  # noqa: S308
        except CaptureEvent.DoesNotExist:
            return "-"

    @admin.display(description="User")
    def capturing_user(self, obj: CaptureLog) -> str:
        user = obj.raw_capture_event.badge.user
        url = reverse("admin:accounts_user_change", args=[user.id])
        return mark_safe(f'<a href="{url}">{user}</a>')  # noqa: S308

    @admin.display(description="Badge")
    def badge(self, obj: CaptureLog) -> str:
        badge = obj.raw_capture_event.badge
        url = reverse("admin:accounts_badge_change", args=[badge.id])
        return mark_safe(f'<a href="{url}">{badge}</a>')  # noqa: S308

    @admin.display(description="Hexpansion")
    def hexpansion(self, obj: CaptureLog) -> str:
        hexpansion = obj.raw_capture_event.hexpansion
        url = reverse("admin:hexpansion_hexpansion_change", args=[hexpansion.id])
        return mark_safe(f'<a href="{url}">{hexpansion}</a>')  # noqa: S308


class LeaderboardAdmin(admin.ModelAdmin):
    filter_horizontal = ("members",)
    list_display = ("display_name", "owner")
    search_fields = ("display_name", "owner__display_name", "owner__username")
    readonly_fields = ("id", "created_at", "created_by", "updated_at", "member_count")
    fieldsets = (
        (None, {"fields": ("display_name", "owner", "enable_invites", "member_count", "members")}),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    @admin.display(description="Member Count")
    def member_count(self, obj: Leaderboard) -> int:
        return obj.members.count()

    def save_form(self, request: HttpRequest, form: ModelForm, change: bool) -> Leaderboard:  # noqa: FBT001
        created = form.instance.created_at is None
        instance = super().save_form(request, form, change)
        if created:
            instance.created_by = request.user
        return instance


admin.site.register(Location, LocationAdmin)
admin.site.register(RawCaptureEvent, RawCaptureEventAdmin)
admin.site.register(CaptureEvent, CaptureEventAdmin)
admin.site.register(CaptureLog, CaptureLogAdmin)
admin.site.register(Leaderboard, LeaderboardAdmin)
