# Generated by Django 5.0.6 on 2024-05-15 13:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quest", "0003_simplify_locations"),
    ]

    operations = [
        migrations.AddField(
            model_name="captureevent",
            name="score",
            field=models.IntegerField(
                choices=[
                    (10, "Easy"),
                    (15, "Medium"),
                    (20, "Hard"),
                    (30, "Insane"),
                    (50, "Impossible"),
                ],
                default=10,
                editable=False,
            ),
            preserve_default=False,
        ),
    ]
