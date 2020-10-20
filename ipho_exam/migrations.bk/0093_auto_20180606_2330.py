from django.db import migrations, models
import ipho_exam.utils.natural_id


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_exam", "0092_merge"),
    ]

    operations = [
        migrations.AlterField(
            model_name="figure",
            name="fig_id",
            field=models.URLField(
                max_length=100,
                unique=True,
                db_index=True,
                default=ipho_exam.utils.natural_id.generate_id,
            ),
        ),
    ]
