# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0030_language_style'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pdf', models.FileField(upload_to=b'', blank=True)),
                ('status', models.CharField(default=b'O', max_length=1, choices=[(b'O', b'In progress'), (b'L', b'Locked'), (b'S', b'Submitted')])),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='language',
            name='is_pdf',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pdfnode',
            name='language',
            field=models.ForeignKey(to='ipho_exam.Language'),
        ),
        migrations.AddField(
            model_name='pdfnode',
            name='question',
            field=models.ForeignKey(to='ipho_exam.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='pdfnode',
            unique_together=set([('question', 'language')]),
        ),
    ]
