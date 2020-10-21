from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_marking", "0002_auto_20160423_1631"),
    ]

    operations = [
        migrations.RenameField(
            model_name="marking",
            old_name="question_points",
            new_name="marking_meta",
        ),
    ]
