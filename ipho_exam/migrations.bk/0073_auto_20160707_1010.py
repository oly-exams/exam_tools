# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Exam = apps.get_model("ipho_exam", "Exam")
    Student = apps.get_model("ipho_core", "Student")
    Place = apps.get_model("ipho_exam", "Place")
    for exam in Exam.objects.using(db_alias).all():
        for student in Student.objects.using(db_alias).all():
            Place(exam=exam, student=student, name='CHANGEME').save()


def backwards_func(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0072_auto_20160706_2249'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
