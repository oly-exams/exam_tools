from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0007_populate_delegation2"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="language",
            name="delegation",
        ),
    ]
