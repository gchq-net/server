from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import migrations, models

import gchqnet.accounts.tokens

if TYPE_CHECKING:
    from django.apps.registry import Apps
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def generate_api_tokens(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model("accounts", "User")  # noqa: N806

    for user in User.objects.all():
        user.api_token = gchqnet.accounts.tokens.generate_api_token()
        user.save(update_fields=["api_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="api_token",
            field=models.CharField(
                blank=True,
                default="",
                max_length=32,
                verbose_name="API Token",
            ),
        ),
        migrations.RunPython(generate_api_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="api_token",
            field=models.CharField(
                default=gchqnet.accounts.tokens.generate_api_token,
                max_length=32,
                unique=True,
                verbose_name="API Token",
            ),
        ),
    ]
