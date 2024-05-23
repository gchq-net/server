import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("achievements", "0002_add_first_to_capture_achievement"),
        ("quest", "0004_add_submission_fields_to_raw_capture"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="scorerecord",
            name="ensure_linked_event",
        ),
        migrations.AddField(
            model_name="scorerecord",
            name="first_capture_event",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="score_record",
                to="achievements.firsttocaptureachievementevent",
            ),
        ),
        migrations.AddConstraint(
            model_name="scorerecord",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("capture_event__isnull", False),
                    ("basic_achievement_event__isnull", False),
                    ("first_capture_event__isnull", False),
                    _connector="OR",
                ),
                name="ensure_linked_event",
            ),
        ),
    ]
