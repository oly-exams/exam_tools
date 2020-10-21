from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0028_remove_question_points"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feedback",
            name="status",
            field=models.CharField(
                default=b"S",
                max_length=1,
                choices=[
                    (b"S", b"Submitted"),
                    (b"P", b"In progress"),
                    (b"R", b"Resolved"),
                ],
            ),
        ),
    ]
