from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0076_auto_20160707_2144"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attributechange",
            name="node",
            field=models.OneToOneField(to="ipho_exam.TranslationNode"),
        ),
        migrations.AlterUniqueTogether(
            name="attributechange",
            unique_together=set(),
        ),
        migrations.AlterIndexTogether(
            name="attributechange",
            index_together=set(),
        ),
        migrations.RemoveField(
            model_name="attributechange",
            name="language",
        ),
    ]
