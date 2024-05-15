from django.contrib import admin
from django.forms import ModelForm
from django.http import HttpRequest

from .models import BasicAchievement, BasicAchievementEvent


class BasicAchievementAdmin(admin.ModelAdmin):
    model = BasicAchievement
    list_display = ("display_name", "hide_display_name", "difficulty")
    list_filter = ("difficulty", "hide_display_name")
    readonly_fields = ("id", "created_at", "created_by", "updated_at")
    search_fields = ("display_name", "description")
    fieldsets = (
        (None, {"fields": ("display_name", "hide_display_name", "difficulty", "description")}),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    def save_form(self, request: HttpRequest, form: ModelForm, change: bool) -> BasicAchievement:  # noqa: FBT001
        created = form.instance.created_at is None
        instance = super().save_form(request, form, change)
        if created:
            instance.created_by = request.user

        # Update all events with new difficulty
        instance.events.update(score=instance.difficulty)
        return instance

    def has_delete_permission(self, request: HttpRequest, obj: BasicAchievement | None = None) -> bool:
        """Disable manual deletion of basic achievements."""
        return False


class BasicAchievementEventAdmin(admin.ModelAdmin):
    model = BasicAchievementEvent
    list_display = ("achievement", "user", "created_at")
    readonly_fields = ("id", "score", "created_at", "created_by", "updated_at")
    fieldsets = (
        (None, {"fields": ("achievement", "user", "score")}),
        ("Database Info", {"classes": ["collapse"], "fields": ("id", "created_at", "created_by", "updated_at")}),
    )

    def save_form(self, request: HttpRequest, form: ModelForm, change: bool) -> BasicAchievement:  # noqa: FBT001
        created = form.instance.created_at is None
        form.instance.score = form.instance.achievement.difficulty
        instance = super().save_form(request, form, change)
        if created:
            instance.created_by = request.user
        return instance


admin.site.register(BasicAchievement, BasicAchievementAdmin)
admin.site.register(BasicAchievementEvent, BasicAchievementEventAdmin)
