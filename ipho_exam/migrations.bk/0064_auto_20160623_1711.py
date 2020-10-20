from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0063_auto_20160623_1659"),
    ]

    operations = [
        migrations.AlterField(
            model_name="figure",
            name="name",
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name="language",
            name="name",
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterField(
            model_name="question",
            name="name",
            field=models.CharField(max_length=100, db_index=True),
        ),
        migrations.AlterIndexTogether(
            name="document",
            index_together={("exam", "student", "position")},
        ),
        migrations.AlterIndexTogether(
            name="examaction",
            index_together={("exam", "delegation", "action")},
        ),
        migrations.AlterIndexTogether(
            name="language",
            index_together={("name", "delegation")},
        ),
        migrations.AlterIndexTogether(
            name="like",
            index_together={("delegation", "feedback")},
        ),
        migrations.AlterIndexTogether(
            name="pdfnode",
            index_together={("question", "language")},
        ),
        migrations.AlterIndexTogether(
            name="studentsubmission",
            index_together={("student", "exam", "language")},
        ),
        migrations.AlterIndexTogether(
            name="translationnode",
            index_together={("question", "language")},
        ),
        migrations.AlterIndexTogether(
            name="versionnode",
            index_together={("question", "language", "version")},
        ),
    ]
