# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=3, null=True, blank=True)),
                ('choice_text', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField(null=True, blank=True)),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date published')),
                ('end_date', models.DateTimeField(null=True, verbose_name=b'end date', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.ForeignKey(to='ipho_poll.Choice')),
                ('question', models.ForeignKey(to='ipho_poll.Question')),
            ],
        ),
        migrations.CreateModel(
            name='VotingRight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='voting_right',
            field=models.ForeignKey(to='ipho_poll.VotingRight'),
        ),
        migrations.AddField(
            model_name='choice',
            name='question',
            field=models.ForeignKey(to='ipho_poll.Question'),
        ),
    ]
