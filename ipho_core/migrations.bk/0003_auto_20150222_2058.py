from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0002_student_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="delegation",
            name="members",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
