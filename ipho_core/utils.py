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

import re
import html

__all__ = ("is_ajax", "unescape_entities")


def is_ajax(request):
    """
    Utility to replace the deprecated Django is_ajax.
    """
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def unescape_entities(text):
    """The 'django.utils.unescape_entities' function, which was removed in 4.0."""
    return _entity_re.sub(_replace_entity, str(text))


_entity_re = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")


def _replace_entity(match):
    text = match[1]
    if text[0] == "#":
        text = text[1:]
        try:
            if text[0] in "xX":
                c = int(text[1:], 16)  # pylint: disable=invalid-name
            else:
                c = int(text)  # pylint: disable=invalid-name
            return chr(c)
        except ValueError:
            return match[0]
    else:
        try:
            return chr(html.entities.name2codepoint[text])
        except KeyError:
            return match[0]
