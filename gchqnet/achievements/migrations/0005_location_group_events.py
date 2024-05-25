# Generated by Django 5.0.6 on 2024-05-25 21:07

import uuid

import django.db.models.deletion
import django_prometheus.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0004_add_location_groups"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LocationGroupAchievementEvent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        verbose_name="Database ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "location_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="achievements.locationgroup",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="location_group_achievement_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("created_at",),
            },
            bases=(
                django_prometheus.models.ExportModelOperationsMixin("location_group_achievement_event"),
                models.Model,
            ),
        ),
        migrations.AddConstraint(
            model_name="locationgroupachievementevent",
            constraint=models.UniqueConstraint(
                fields=("location_group", "user"),
                name="one_event_per_user_per_location_group",
            ),
        ),
    ]
