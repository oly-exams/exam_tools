from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0016_auto_20151109_1835"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="examdelegationsubmission",
            unique_together={("exam", "delegation")},
        ),
        migrations.AlterUniqueTogether(
            name="studentsubmission",
            unique_together={("student", "exam", "language")},
        ),
    ]
