# Generated by Django 5.0.6 on 2024-05-28 21:17

from django.db import migrations, models

import gchqnet.quest.models.location


class Migration(migrations.Migration):
    dependencies = [
        ("quest", "0009_location_group_events"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="install_image",
            field=models.ImageField(
                null=True,
                upload_to=gchqnet.quest.models.location.UploadToPathAndRename(),
            ),
        ),
    ]
