# Generated by Django 5.0.6 on 2024-05-19 07:51

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PlannedLocation",
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
                (
                    "display_name",
                    models.CharField(
                        blank=True,
                        help_text="This name is shown to players who have captured the location.",
                        max_length=30,
                        verbose_name="Display name",
                    ),
                ),
                (
                    "hint",
                    models.CharField(
                        blank=True,
                        help_text="This name is shown to players to help them find the location.",
                        max_length=60,
                        verbose_name="Hint",
                    ),
                ),
                (
                    "internal_name",
                    models.CharField(
                        help_text="This name is shown to admins and should be descriptive.",
                        max_length=50,
                        unique=True,
                        verbose_name="Internal name",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Further description of the planned location of the installation.",
                    ),
                ),
                (
                    "difficulty",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (10, "Easy"),
                            (15, "Medium"),
                            (20, "Hard"),
                            (30, "Insane"),
                            (50, "Impossible"),
                        ],
                        null=True,
                    ),
                ),
                (
                    "lat",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-90),
                            django.core.validators.MaxValueValidator(90),
                        ],
                        verbose_name="Latitude",
                    ),
                ),
                (
                    "long",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=8,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-180),
                            django.core.validators.MaxValueValidator(180),
                        ],
                        verbose_name="Longitude",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("internal_name",),
            },
        ),
    ]