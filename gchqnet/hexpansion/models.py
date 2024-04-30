import uuid

from django.db import models


class Hexpansion(models.Model):
    id = models.UUIDField("Database ID", primary_key=True, default=uuid.uuid4, editable=False)

    human_identifier = models.CharField(
        "Human Identifier",
        max_length=6,
        help_text="The identifier written on the device for human identification",
        unique=True,
    )
    eeprom_serial_number = models.SmallIntegerField("EEPROM Serial Number", unique=True)
    serial_number = models.UUIDField("Serial Number", help_text="Serial Number of ATSHA204, encoded as 128-bit UUID")
    hardware_revision = models.CharField("Hardware Version", max_length=4, choices=[("1", "rev 1.0")], default="1")

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("human_identifier",)

    def __str__(self) -> str:
        return f"Hexpansion {self.human_identifier}"
