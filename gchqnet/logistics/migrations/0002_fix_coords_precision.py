import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("logistics", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plannedlocation",
            name="lat",
            field=models.DecimalField(
                blank=True,
                decimal_places=13,
                max_digits=16,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ],
                verbose_name="Latitude",
            ),
        ),
        migrations.AlterField(
            model_name="plannedlocation",
            name="long",
            field=models.DecimalField(
                blank=True,
                decimal_places=13,
                max_digits=16,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ],
                verbose_name="Longitude",
            ),
        ),
    ]
