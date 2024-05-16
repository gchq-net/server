from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from django.db import models

from gchqnet.quest.repository import get_private_scoreboard

if TYPE_CHECKING:  # pragma: nocover
    from gchqnet.accounts.models import User


class Leaderboard(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(
        "Display name",
        max_length=40,
    )

    owner = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="leaderboards_created")
    members = models.ManyToManyField("accounts.User", related_name="leaderboards")
    enable_invites = models.BooleanField(
        "Enable Invites",
        help_text="Allow other players to join this leaderboard using an invite link",
        default=True,
    )

    # The User that created the leaderboard is the admin.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.display_name

    @property
    def scores(self) -> models.QuerySet[User]:
        return get_private_scoreboard(self)
