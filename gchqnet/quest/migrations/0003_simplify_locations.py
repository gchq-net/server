from __future__ import annotations

from typing import TYPE_CHECKING

import django.db.models.deletion
from django.db import migrations, models

if TYPE_CHECKING:  # pragma: nocover
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def remove_installation_field(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Location = apps.get_model("quest", "Location")  # noqa: N806

    for location in Location.objects.select_related("installation").all():
        Location.objects.filter(id=location.id).update(hexpansion=location.installation.hexpansion)


class Migration(migrations.Migration):
    dependencies = [
        ("hexpansion", "0001_initial"),
        ("quest", "0002_leaderboard"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="hexpansion",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="location",
                to="hexpansion.hexpansion",
            ),
        ),
        migrations.AddField(
            model_name="location",
            name="hint",
            field=models.CharField(
                default="Hint",
                help_text="This name is shown to players to help them find the location.",
                max_length=60,
                verbose_name="Hint",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="captureevent",
            name="location",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="capture_events",
                to="quest.location",
            ),
        ),
        migrations.RunPython(
            remove_installation_field,
            migrations.RunPython.noop,
            elidable=True,
        ),
        migrations.AlterField(
            model_name="location",
            name="hexpansion",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="location",
                to="hexpansion.hexpansion",
            ),
        ),
        migrations.DeleteModel(
            name="LocationInstallation",
        ),
    ]
