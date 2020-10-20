from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0004_auto_20150222_2105"),
    ]

    operations = [
        migrations.CreateModel(
            name="IphoPerm",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("is_leader", "Is a leader"),
                    ("is_staff", "Is an organizer"),
                ),
            },
            bases=(models.Model,),
        ),
    ]
