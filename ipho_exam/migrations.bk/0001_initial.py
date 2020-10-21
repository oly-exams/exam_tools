from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Exam",
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
                ("name", models.CharField(max_length=100)),
                (
                    "active",
                    models.BooleanField(
                        default=True, help_text=b"Only active exams are editable."
                    ),
                ),
                (
                    "hidden",
                    models.BooleanField(
                        default=False,
                        help_text=b"Is the exam hidden for the delegations?",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Language",
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
                ("name", models.CharField(unique=True, max_length=100)),
                ("hidden", models.BooleanField(default=False)),
                ("versioned", models.BooleanField(default=False)),
                ("delegation", models.ManyToManyField(to="ipho_core.Delegation")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Question",
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
                ("name", models.CharField(max_length=100)),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        help_text=b"Sortign index inside one exam"
                    ),
                ),
                ("exam", models.ForeignKey(to="ipho_exam.Exam")),
            ],
            options={
                "ordering": ["position"],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="TranslationNode",
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
                ("text", models.TextField()),
                (
                    "status",
                    models.CharField(
                        max_length=1,
                        choices=[
                            (b"O", b"open"),
                            (b"L", b"locked"),
                            (b"S", b"submitted"),
                        ],
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("language", models.ForeignKey(to="ipho_exam.Language")),
                ("question", models.ForeignKey(to="ipho_exam.Question")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="VersionNode",
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
                ("text", models.TextField()),
                ("version", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        max_length=1,
                        choices=[(b"P", b"proposal"), (b"C", b"confirmed")],
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
                ("language", models.ForeignKey(to="ipho_exam.Language")),
                ("question", models.ForeignKey(to="ipho_exam.Question")),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
