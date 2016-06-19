# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0054_auto_20160606_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='polyglossia',
            field=models.CharField(default=b'english', max_length=100, choices=[(b'albanian', b'Albanian'), (b'amharic', b'Amharic'), (b'arabic', b'Arabic'), (b'armenian', b'Armenian'), (b'asturian', b'Asturian'), (b'bahasai', b'Bahasai'), (b'bahasam', b'Bahasam'), (b'basque', b'Basque'), (b'bengali', b'Bengali'), (b'brazilian', b'Brazilian'), (b'breton', b'Breton'), (b'bulgarian', b'Bulgarian'), (b'catalan', b'Catalan'), (b'coptic', b'Coptic'), (b'croatian', b'Croatian'), (b'czech', b'Czech'), (b'danish', b'Danish'), (b'divehi', b'Divehi'), (b'dutch', b'Dutch'), (b'english', b'English'), (b'esperanto', b'Esperanto'), (b'estonian', b'Estonian'), (b'farsi', b'Farsi'), (b'finnish', b'Finnish'), (b'french', b'French'), (b'friulan', b'Friulan'), (b'galician', b'Galician'), (b'german', b'German'), (b'greek', b'Greek'), (b'hebrew', b'Hebrew'), (b'hindi', b'Hindi'), (b'icelandic', b'Icelandic'), (b'interlingua', b'Interlingua'), (b'irish', b'Irish'), (b'italian', b'Italian'), (b'kannada', b'Kannada'), (b'lao', b'Lao'), (b'latin', b'Latin'), (b'latvian', b'Latvian'), (b'lithuanian', b'Lithuanian'), (b'lsorbian', b'Lsorbian'), (b'magyar', b'Magyar'), (b'malayalam', b'Malayalam'), (b'marathi', b'Marathi'), (b'nko', b'Nko'), (b'norsk', b'Norsk'), (b'nynorsk', b'Nynorsk'), (b'occitan', b'Occitan'), (b'piedmontese', b'Piedmontese'), (b'polish', b'Polish'), (b'portuges', b'Portuges'), (b'romanian', b'Romanian'), (b'romansh', b'Romansh'), (b'russian', b'Russian'), (b'samin', b'Samin'), (b'sanskrit', b'Sanskrit'), (b'scottish', b'Scottish'), (b'serbian', b'Serbian'), (b'slovak', b'Slovak'), (b'slovenian', b'Slovenian'), (b'spanish', b'Spanish'), (b'swedish', b'Swedish'), (b'syriac', b'Syriac'), (b'tamil', b'Tamil'), (b'telugu', b'Telugu'), (b'thai', b'Thai'), (b'tibetan', b'Tibetan'), (b'turkish', b'Turkish'), (b'turkmen', b'Turkmen'), (b'ukrainian', b'Ukrainian'), (b'urdu', b'Urdu'), (b'usorbian', b'Usorbian'), (b'vietnamese', b'Vietnamese'), (b'welsh', b'Welsh'), (b'custom', b'Other')]),
        ),
    ]
