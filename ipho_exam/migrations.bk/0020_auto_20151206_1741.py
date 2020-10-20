from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0019_question_type"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="language",
            unique_together={("name", "delegation")},
        ),
    ]
