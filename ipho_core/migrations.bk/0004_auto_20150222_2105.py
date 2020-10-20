# pylint: skip-file

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0003_auto_20150222_2058"),
    ]

    operations = [
        migrations.RenameField(
            model_name="student",
            old_name="firstname",
            new_name="first_name",
        ),
        migrations.RenameField(
            model_name="student",
            old_name="lastname",
            new_name="last_name",
        ),
    ]
