from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_poll", "0004_question_feedbacks"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together={("question", "voting_right")},
        ),
    ]
