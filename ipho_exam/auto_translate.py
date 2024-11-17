# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import re
from hashlib import md5

import deepl
from django.conf import settings
from google.api_core.exceptions import BadRequest
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from ipho_exam.models import CachedAutoTranslation

django_logger = logging.getLogger("django.request")
logger = logging.getLogger("exam_tools")


AUTO_TRANSLATE_LANGUAGE_LIST = [
    lang["language"] for lang in settings.AUTO_TRANSLATE_LANGUAGES
]


class SpanReplacer:
    """Replaces spans with empty spans"""

    def __init__(self, span_class):
        self.span_class = span_class
        self.matches = []
        self.i = -1
        self.replace_pattern = (
            r'<\s*span[^>]*\sclass\s*=\s*"' + span_class + r'"\s*>.*?<\s*/\s*span\s*>'
        )
        self.readd_pattern = (
            r"<\s*span\s*data-"
            + span_class
            + r'-oly\s*=\s*"([0-9]*)"\s*>\s*<\s*\/\s*span\s*>'
        )

    def _repl(self, match):
        self.matches.append(match.group(0))
        self.i += 1
        return f'<span data-{self.span_class}-oly="{self.i}"></span>'

    def _readd(self, match):
        num = int(match.group(1))
        if num < len(self.matches):
            return self.matches[num]
        return match.group(0)

    def replace_span(self, raw_text):
        return re.sub(self.replace_pattern, self._repl, raw_text)

    def readd_span(self, raw_translated_text):
        return re.sub(self.readd_pattern, self._readd, raw_translated_text)


def get_cached_translation(from_lang_style, to_lang, text):
    hash_ = md5((from_lang_style + to_lang + text).encode("utf-8")).hexdigest()
    cachedtr = CachedAutoTranslation.objects.filter(source_and_lang_hash=hash_).first()
    if cachedtr is not None:
        cachedtr.hits += 1
        cachedtr.save()
        return cachedtr.target_text
    return None


def save_cached_translation(
    from_lang_style, from_lang, from_length, to_lang, text, raw_translated_text
):
    hash_ = md5((from_lang_style + to_lang + text).encode("utf-8")).hexdigest()
    cachedtr, _ = CachedAutoTranslation.objects.get_or_create(
        source_and_lang_hash=hash_, source_length=from_length
    )
    cachedtr.source_lang = from_lang
    cachedtr.target_lang = to_lang
    cachedtr.target_text = raw_translated_text
    cachedtr.save()


def translate_google(from_lang, to_lang, text):
    json_cred = json.loads(
        getattr(settings, "GOOGLE_TRANSLATE_SERVICE_ACCOUNT_KEY", "{}")
    )
    translate_client = translate.Client(
        credentials=service_account.Credentials.from_service_account_info(json_cred)
    )

    google_from_lang = from_lang if from_lang else None

    # get translated text
    try:
        cloud_response = translate_client.translate(
            text, target_language=to_lang, source_language=google_from_lang
        )
    except BadRequest as err:
        # log error
        django_logger.error(err)
        logger.error(err)
        return None
    return cloud_response["translatedText"]


def find_best_matching_deepl_lang(lang, langs):
    ulang = lang.upper()
    parts = ulang.split("-")
    # TODO: Should we allow variants?
    # As in, use fr-CH where fr-FR is given/requested?
    if ulang in langs:
        return ulang
    if "zh" in lang:
        return None
    if len(parts) == 1:
        if ulang + "-" + ulang in langs:
            return ulang + "-" + ulang
        for lng in langs:
            if ulang == lng.split("-")[0]:
                return lng
    # Workaround for trad/simplified chinese
    if len(parts) > 1 and parts[0] in langs:
        return parts[0]
    return None


def translate_deepl(from_lang, to_lang, text):
    if from_lang:
        from_lang = find_best_matching_deepl_lang(
            from_lang, settings.DEEPL_SOURCE_LANGUAGES
        )
        if from_lang is None:
            return None

    to_lang = find_best_matching_deepl_lang(to_lang, settings.DEEPL_TARGET_LANGUAGES)
    if to_lang is None:
        return None

    translate_client = deepl.Translator(settings.DEEPL_API_KEY)

    # translate
    try:
        translated_text = translate_client.translate_text(
            text, source_lang=from_lang, target_lang=to_lang, tag_handling="html"
        ).text
    except (ValueError, TypeError, deepl.DeepLException) as err:
        # log error and use google as a fallback
        django_logger.error(err)
        logger.error(err)
        return None
    return translated_text


def auto_translate_helper(raw_text, from_lang_obj, to_lang, delegation):
    # sanitize to_lang and from_lang
    if from_lang_obj.style is not None:
        from_lang = settings.STYLES_TO_AUTO_TRANSLATE_MAPPING[from_lang_obj.style]
        from_lang_style = from_lang_obj.style
    else:
        from_lang = ""
        from_lang_style = "None"
    if to_lang == from_lang:
        return {"text": raw_text}
    if raw_text == "":
        return {"text": raw_text}
    if to_lang not in AUTO_TRANSLATE_LANGUAGE_LIST:
        raise ValueError(
            f"Target Language {to_lang} not in AUTO_TRANSLATE_LANGUAGE_LIST"
        )
    if from_lang != "" and from_lang not in AUTO_TRANSLATE_LANGUAGE_LIST:
        raise ValueError(
            f"Source Language {from_lang} not in AUTO_TRANSLATE_LANGUAGE_LIST"
        )

    # replace math with empty spans
    math_replacer = SpanReplacer("math-tex")
    rtl_replacer = SpanReplacer("lang-ltr")
    math_text = math_replacer.replace_span(raw_text)
    text = rtl_replacer.replace_span(math_text)

    # update translate_char_count
    from_length = len(text)
    if delegation is not None:
        delegation.auto_translate_char_count += from_length
        delegation.save()

    # get cached text
    raw_translated_text = get_cached_translation(from_lang_style, to_lang, text)

    # translate if no cached text exists
    if raw_translated_text is None:
        # prefer deepl
        raw_translated_text = translate_deepl(from_lang, to_lang, text)
        if raw_translated_text is None:
            raw_translated_text = translate_google(from_lang, to_lang, text)
            if raw_translated_text is None:
                return {"error": "Translation not supported"}
        # cache result
        save_cached_translation(
            from_lang_style, from_lang, from_length, to_lang, text, raw_translated_text
        )

    # readd math
    translated_text_math = math_replacer.readd_span(raw_translated_text)
    translated_text = rtl_replacer.readd_span(translated_text_math)

    return {"text": translated_text}
