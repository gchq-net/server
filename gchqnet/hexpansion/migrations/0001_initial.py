# Generated by Django 5.0.6 on 2024-05-18 18:12

import uuid

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
            name="Hexpansion",
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
                    "human_identifier",
                    models.CharField(
                        help_text="The identifier written on the device for human identification",
                        max_length=6,
                        unique=True,
                        verbose_name="Human Identifier",
                    ),
                ),
                (
                    "eeprom_serial_number",
                    models.SmallIntegerField(unique=True, verbose_name="EEPROM Serial Number"),
                ),
                (
                    "serial_number",
                    models.UUIDField(
                        help_text="Serial Number of ATSHA204, encoded as 128-bit UUID",
                        verbose_name="Serial Number",
                    ),
                ),
                (
                    "hardware_revision",
                    models.CharField(
                        choices=[("1", "rev 1.0")],
                        default="1",
                        max_length=4,
                        verbose_name="Hardware Version",
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
            ],
            options={
                "ordering": ("human_identifier",),
            },
        ),
    ]
