# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def move_figures(apps, schema_editor):
    Figure = apps.get_model('ipho_exam', 'Figure')
    CompiledFigure = apps.get_model('ipho_exam', 'CompiledFigure')

    for f in Figure.objects.all():
        if not isinstance(f, CompiledFigure):
            cf = CompiledFigure(id=f.id, name=f.name, content=f.content, params=f.params)
            cf.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0079_compiledfigure'),
    ]

    operations = [migrations.RunPython(move_figures)]
