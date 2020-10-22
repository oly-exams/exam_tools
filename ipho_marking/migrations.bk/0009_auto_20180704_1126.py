from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("ipho_marking", "0008_auto_20180318_0929"),
    ]

    operations = [
        migrations.AlterField(
            model_name="marking",
            name="points",
            field=models.DecimalField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(0.0)],
                max_digits=8,
                decimal_places=2,
            ),
        ),
    ]
