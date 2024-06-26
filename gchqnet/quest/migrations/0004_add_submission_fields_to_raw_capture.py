# Generated by Django 5.0.6 on 2024-05-21 20:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quest", "0003_fix_coords_rounding"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawcaptureevent",
            name="app_rev",
            field=models.CharField(max_length=20, verbose_name="App Revision"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="fw_rev",
            field=models.CharField(max_length=20, verbose_name="Firmware Revision"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="hmac",
            field=models.CharField(
                max_length=64,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[0-9a-f]{64}$",
                        "The HMAC does not appear to be in the correct format.",
                    )
                ],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="rand",
            field=models.UUIDField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="wifi_bssid",
            field=models.CharField(
                help_text="IEEE 802 format, e.g 12-34-56-78-90-AB",
                max_length=17,
                validators=[
                    django.core.validators.RegexValidator(
                        "^([0-9A-F]{2}[-]){5}([0-9A-F]{2})$",
                        "The MAC address does not appear to be in the correct format.",
                    )
                ],
                verbose_name="WiFi BSSID",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="wifi_channel",
            field=models.PositiveSmallIntegerField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="rawcaptureevent",
            name="wifi_rssi",
            field=models.IntegerField(),
            preserve_default=False,
        ),
    ]
