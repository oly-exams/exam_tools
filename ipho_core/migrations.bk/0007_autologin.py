import uuid
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ipho_core", "0006_auto_20160207_2210"),
    ]

    operations = [
        migrations.CreateModel(
            name="AutoLogin",
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
                (
                    "token",
                    models.UUIDField(default=uuid.uuid4, editable=False, db_index=True),
                ),
                ("user", models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
