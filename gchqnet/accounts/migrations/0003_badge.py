# Generated by Django 5.0.4 on 2024-04-29 18:11

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_case_insensitive_unique_display_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Badge",
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
                    "mac_address",
                    models.CharField(
                        help_text="IEEE 802 format, e.g 12-34-56-78-90-AB-CD",
                        max_length=17,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$",
                                "The MAC address does not appear to be in the correct format.",
                            )
                        ],
                        verbose_name="MAC Address",
                    ),
                ),
                (
                    "is_enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Is the badge enabled? i.e can it be used to capture locations?",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="badges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]