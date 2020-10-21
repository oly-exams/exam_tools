from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0007_autologin"),
        ("ipho_exam", "0030_language_style"),
    ]

    operations = [
        migrations.CreateModel(
            name="Marking",
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
                ("points", models.FloatField()),
                ("comment", models.TextField()),
                (
                    "version",
                    models.CharField(
                        max_length=1,
                        choices=[
                            (b"O", b"Organizers"),
                            (b"D", b"Delegation"),
                            (b"F", b"Final"),
                        ],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuestionPoints",
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
                ("name", models.CharField(max_length=2)),
                ("max_points", models.FloatField()),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        help_text=b"Sorting index inside one question"
                    ),
                ),
                ("question", models.ForeignKey(to="ipho_exam.Question")),
            ],
        ),
        migrations.AddField(
            model_name="marking",
            name="question_points",
            field=models.ForeignKey(to="ipho_marking.QuestionPoints"),
        ),
        migrations.AddField(
            model_name="marking",
            name="student",
            field=models.ForeignKey(to="ipho_core.Student"),
        ),
    ]
