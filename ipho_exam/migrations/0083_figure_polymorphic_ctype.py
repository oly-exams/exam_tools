# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def forwards_func(apps, schema_editor):
    Figure = apps.get_model('ipho_exam', 'Figure')
    CompiledFigure = apps.get_model('ipho_exam', 'CompiledFigure')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    new_ct = ContentType.objects.get_for_model(CompiledFigure)
    Figure.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=new_ct)


def backwards_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipho_exam', '0082_auto_20170305_1640'),
    ]

    operations = [
        migrations.AddField(
            model_name='figure',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_ipho_exam.figure_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
