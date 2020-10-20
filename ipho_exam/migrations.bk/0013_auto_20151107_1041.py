from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0012_exam_feedback_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="position",
            field=models.PositiveSmallIntegerField(
                help_text=b"Sorting index inside one exam"
            ),
            preserve_default=True,
        ),
    ]
