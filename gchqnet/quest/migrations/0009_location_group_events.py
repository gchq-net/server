# Generated by Django 5.0.6 on 2024-05-25 21:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0005_location_group_events"),
        ("quest", "0008_rawcaptureevent_rand_new"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="scorerecord",
            name="ensure_linked_event",
        ),
        migrations.AddField(
            model_name="scorerecord",
            name="location_group_achievement_event",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="score_record",
                to="achievements.locationgroupachievementevent",
            ),
        ),
        migrations.AddConstraint(
            model_name="scorerecord",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("capture_event__isnull", False),
                    ("basic_achievement_event__isnull", False),
                    ("first_capture_event__isnull", False),
                    ("location_group_achievement_event__isnull", False),
                    _connector="OR",
                ),
                name="ensure_linked_event",
            ),
        ),
    ]
