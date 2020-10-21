from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Delegation",
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
                ("name", models.CharField(unique=True, max_length=3)),
                ("country", models.CharField(unique=True, max_length=100)),
                ("members", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Student",
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
                ("firstname", models.CharField(max_length=200)),
                ("lastname", models.CharField(max_length=200)),
                ("delegation", models.ForeignKey(to="ipho_core.Delegation")),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
