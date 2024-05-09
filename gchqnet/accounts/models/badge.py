from __future__ import annotations

import uuid

from django.core.validators import RegexValidator
from django.db import models


class Badge(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)
    mac_address = models.CharField(
        "MAC Address",
        max_length=17,
        unique=True,
        help_text="IEEE 802 format, e.g 12-34-56-78-90-AB-CD",
        validators=[
            RegexValidator(
                "^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$", "The MAC address does not appear to be in the correct format."
            )
        ],
    )

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="badges")
    is_enabled = models.BooleanField(
        default=True, help_text="Is the badge enabled? i.e can it be used to capture locations?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.mac_address

    @property
    def model_name(self) -> str:
        return "EMF Tildagon (2024)"
