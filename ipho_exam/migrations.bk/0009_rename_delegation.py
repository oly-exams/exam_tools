from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0004_auto_20150222_2105"),
        ("ipho_exam", "0008_remove_language_delegation"),
    ]

    operations = [
        migrations.RenameField(
            model_name="language",
            old_name="delegation2",
            new_name="delegation",
        ),
    ]
