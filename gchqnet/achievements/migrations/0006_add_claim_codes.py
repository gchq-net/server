from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations, models

import gchqnet.achievements.models

if TYPE_CHECKING:
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    from django.db.migrations.state import StateApps


def add_claim_code(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    BasicAchievement = apps.get_model("achievements", "BasicAchievement")

    for achievement in BasicAchievement.objects.all():
        achievement.claim_code = gchqnet.achievements.models.generate_claim_code()
        achievement.save(update_fields=["claim_code"])


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0005_location_group_events"),
    ]

    operations = [
        migrations.AddField(
            model_name="basicachievement",
            name="claim_code",
            field=models.CharField(default=gchqnet.achievements.models.generate_claim_code, max_length=50),
        ),
        migrations.RunPython(
            add_claim_code,
            migrations.RunPython.noop,
            elidable=True,
        ),
        migrations.AlterField(
            model_name="basicachievement",
            name="claim_code",
            field=models.CharField(default=gchqnet.achievements.models.generate_claim_code, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="basicachievement",
            name="award_type",
            field=models.CharField(
                choices=[("internal", "Internal"), ("external", "External"), ("manual", "Manual"), ("claim", "Claim")],
                max_length=8,
            ),
        ),
    ]
