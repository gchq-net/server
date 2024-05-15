from __future__ import annotations

from typing import Any, TypeVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.db.models.functions import DenseRank, Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import WithAnnotations

from gchqnet.accounts.tokens import generate_api_token
from gchqnet.achievements.models import BasicAchievementEvent
from gchqnet.quest.models.captures import CaptureEvent

_T = TypeVar("_T", bound=models.Model)


class UserQuerySet(models.QuerySet[WithAnnotations["User"]]):
    def with_current_score(self) -> UserQuerySet:
        location_difficulty_subquery = models.Subquery(
            CaptureEvent.objects.filter(created_by_id=models.OuterRef("id"))
            .values("created_by_id")
            .annotate(difficulty_sum=models.Sum("score"))
            .values("difficulty_sum")[:1]
        )

        basic_achievements_subquery = models.Subquery(
            BasicAchievementEvent.objects.filter(user_id=models.OuterRef("id"))
            .values("user_id")
            .annotate(
                difficulty_sum=models.Sum("score"),
            )
            .values("difficulty_sum")[:1]
        )

        return self.annotate(
            current_score=sum(
                (
                    models.functions.Coalesce(location_difficulty_subquery, models.Value(0)),
                    models.functions.Coalesce(basic_achievements_subquery, models.Value(0)),
                )
            )
        )

    def with_capture_count(self) -> UserQuerySet:
        return self.annotate(capture_count=models.Count("capture_events"))

    def with_scoreboard_fields(self) -> UserQuerySet:
        qs = self.with_capture_count().with_current_score()
        return qs.annotate(rank=models.Window(expression=DenseRank(), order_by=models.F("current_score").desc()))


class _UserManager(BaseUserManager[_T]):
    """
    Custom UserManager to handle is_staff not existing.

    The following functions are called from other parts of Django, e.g ./manage.py
    """

    def create_user(
        self, username: str, email: str | None = None, password: str | None = None, **extra_fields: Any
    ) -> _T:
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)  # type: ignore[attr-defined]

    def create_superuser(
        self, username: str, email: str | None = None, password: str | None = None, **extra_fields: Any
    ) -> _T:
        extra_fields.setdefault("is_superuser", True)

        if not email:
            raise ValueError("Superuser must have an email.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)  # type: ignore[attr-defined]


class UserManager(_UserManager.from_queryset(UserQuerySet)):  # type: ignore[misc]
    pass


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("account name"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    display_name = models.CharField(
        _("display name"),
        max_length=30,
        unique=True,
        error_messages={
            "unique": _("Another player already has that display name"),
        },
    )

    email = models.EmailField(_("email address"), blank=True)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    api_token = models.CharField("API Token", unique=True, max_length=32, default=generate_api_token)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "display_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(is_superuser=True, email=""),
                name="superuser_must_have_email",
                violation_error_message="Any user with superuser permissions must have an email address",
            ),
            models.UniqueConstraint(
                Lower("display_name"),
                name="unique_display_name",
                violation_error_message="Another player already has that display name",
            ),
        ]

    @property
    def is_staff(self) -> bool:
        return self.is_superuser

    def clean(self) -> None:
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self) -> str:
        return self.display_name

    def get_short_name(self) -> str:
        """Return the short name for the user."""
        return self.display_name

    def email_user(self, subject: str, message: str, from_email: str | None = None, **kwargs: Any) -> None:
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
