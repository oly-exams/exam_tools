from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0027_question_points"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="points",
        ),
    ]
