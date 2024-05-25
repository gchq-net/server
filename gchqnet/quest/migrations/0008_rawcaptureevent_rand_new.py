from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import migrations, models

if TYPE_CHECKING:
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    from django.db.migrations.state import StateApps


def int_to_binary(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    RawCaptureEvent = apps.get_model("quest", "RawCaptureEvent")

    for rce in RawCaptureEvent.objects.all():
        rce.rand_new = rce.rand.int.to_bytes(32, byteorder=sys.byteorder)
        rce.save(update_fields=["rand_new"])


def binary_to_int(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    RawCaptureEvent = apps.get_model("quest", "RawCaptureEvent")

    for rce in RawCaptureEvent.objects.all():
        rce.rand = UUID(int=int.from_bytes(rce.rand_new, sys.byteorder))
        rce.save(update_fields=["rand_new"])


class Migration(migrations.Migration):
    dependencies = [
        ("quest", "0007_remove_wifi_fields_two"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawcaptureevent",
            name="rand_new",
            field=models.BinaryField(max_length=32, null=True),
        ),
        migrations.RunPython(
            int_to_binary,
            binary_to_int,
            elidable=True,
        ),
        migrations.RemoveField(
            model_name="rawcaptureevent",
            name="rand",
        ),
        migrations.AlterField(
            model_name="rawcaptureevent",
            name="rand_new",
            field=models.BinaryField(max_length=32),
        ),
        migrations.RenameField(
            model_name="rawcaptureevent",
            old_name="rand_new",
            new_name="rand",
        ),
    ]
