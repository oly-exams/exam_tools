# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipho_exam', '0087_exam_moderation_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='style',
            field=models.CharField(blank=True, max_length=200, null=True, choices=[('afrikaans', 'Afrikaans'), ('albanian', 'Albanian'), ('amharic', 'Amharic'), ('arabic', 'Arabic'), ('armenian', 'Armenian'), ('asturian', 'Asturian'), ('azerbaijani', 'Azerbaijani'), ('basque', 'Basque'), ('belarusian', 'Belarusian'), ('bengali', 'Bengali'), ('bosnian', 'Bosnian'), ('breton', 'Breton'), ('bulgarian', 'Bulgarian'), ('burmese', 'Burmese'), ('cantonese', 'Cantonese'), ('catalan', 'Catalan'), ('chinese', 'Chinese'), ('coptic', 'Coptic'), ('croatian', 'Croatian'), ('czech', 'Czech'), ('danish', 'Danish'), ('divehi', 'Divehi'), ('dutch', 'Dutch'), ('english', 'English'), ('esperanto', 'Esperanto'), ('filipino', 'Filipino'), ('finnish', 'Finnish'), ('french', 'French'), ('friulian', 'Friulian'), ('galician', 'Galician'), ('georgian', 'Georgian'), ('german', 'German'), ('greek', 'Greek'), ('hebrew', 'Hebrew'), ('hindi', 'Hindi'), ('hungarian', 'Hungarian'), ('icelandic', 'Icelandic'), ('indonesian', 'Indonesian'), ('interlingua', 'Interlingua'), ('irish', 'Irish'), ('italian', 'Italian'), ('japanese', 'Japanese'), ('kannada', 'Kannada'), ('kazakh', 'Kazakh'), ('khmer', 'Khmer'), ('korean', 'Korean'), ('kurdish', 'Kurdish'), ('kyrgyz', 'Kyrgyz'), ('lao', 'Lao'), ('latin', 'Latin'), ('latvian', 'Latvian'), ('lithuanian', 'Lithuanian'), ('luxembourgish', 'Luxembourgish'), ('macedonian', 'Macedonian'), ('magyar', 'Magyar'), ('malay', 'Malay'), ('malayalam', 'Malayalam'), ('malaysian', 'Malaysian'), ('mandarin', 'Mandarin'), ('marathi', 'Marathi'), ('mongolian', 'Mongolian'), ('montenegrin', 'Montenegrin'), ('nepali', 'Nepali'), ('northern sotho', 'Northern Sotho'), ('norwegian bokm\xe5l', 'Norwegian Bokm\xe5l'), ('norwegian nynorsk', 'Norwegian Nynorsk'), ('occitan', 'Occitan'), ('persian', 'Persian'), ('piedmontese', 'Piedmontese'), ('polish', 'Polish'), ('portuguese', 'Portuguese'), ('romanian', 'Romanian'), ('romansh', 'Romansh'), ('russian', 'Russian'), ('sanskrit', 'Sanskrit'), ('scottish', 'Scottish'), ('serbian', 'Serbian'), ('sinhalese', 'Sinhalese'), ('slovak', 'Slovak'), ('slovenian', 'Slovenian'), ('southern ndebele', 'Southern Ndebele'), ('southern sotho', 'Southern Sotho'), ('spanish', 'Spanish'), ('swedish', 'Swedish'), ('syriac', 'Syriac'), ('tajik', 'Tajik'), ('tamil', 'Tamil'), ('telugu', 'Telugu'), ('thai', 'Thai'), ('tibetan', 'Tibetan'), ('tsonga', 'Tsonga'), ('tswana', 'Tswana'), ('turkish', 'Turkish'), ('turkmen', 'Turkmen'), ('ukrainian', 'Ukrainian'), ('urdu', 'Urdu'), ('uzbek', 'Uzbek'), ('venda', 'Venda'), ('vietnamese', 'Vietnamese'), ('welsh', 'Welsh'), ('xhosa', 'Xhosa'), ('zulu', 'Zulu')]),
        ),
    ]