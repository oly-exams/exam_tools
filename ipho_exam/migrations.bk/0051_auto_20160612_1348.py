from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0050_auto_20160608_1016"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrintLog",
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
                    "type",
                    models.CharField(
                        max_length=1, choices=[(b"P", b"Printout"), (b"S", b"Scan")]
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("document", models.ForeignKey(to="ipho_exam.Document")),
            ],
        ),
    ]
