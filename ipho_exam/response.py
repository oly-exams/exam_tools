# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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


import os
import shutil
import logging
from tempfile import mkdtemp
import re
import pypandoc
import latex2mathml.converter


from django.http import HttpResponse
from django.conf import settings
from django.utils.html import escape

from . import tex

TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH")
TEMP_PREFIX = getattr(settings, "ODT_TEMP_PREFIX", "render_odt-")

logger = logging.getLogger("ipho_exam")


def render_odt_response(context, filename, ext_resources):
    contextdict = {}
    for data in context:
        contextdict.update(**data)
    result = None
    output = None
    try:
        tmp = mkdtemp(prefix=TEMP_PREFIX)

        for res in ext_resources:
            res.save(tmp, svg_to_png=True)
            if isinstance(res, tex.FigureExport):
                contextdict["document"] = contextdict["document"].replace(
                    res.figname, f"{tmp}/{res.figname}"
                )

        ref_name = os.path.join(settings.TEMPLATE_PATH, "ipho_exam/odt/reference.odt")
        tpl_name = os.path.join(
            settings.TEMPLATE_PATH, "ipho_exam/odt/tmpl.opendocument"
        )

        output = f"{tmp}/doc.odt"
        logger.debug(
            "Render template '%s' to '%s'", tpl_name, output
        )  # this is recommended by pylint W1201

        mathtex_pattern = re.compile(
            r'<span class="math-tex">\\\((([^<]|<[^/])+)\\\)</span>'
        )

        def tex_to_mathml(txt):
            return mathtex_pattern.sub(
                lambda m: latex2mathml.converter.convert(escape(m.group(1))),
                txt.replace(r"\begin{equation}", '<span class="math-tex">\\(').replace(
                    r"\end{equation}", "\\)</span>"
                ),
            )

        text = tex_to_mathml(contextdict["document"])
        pypandoc.convert_text(
            text,
            format="html",
            to="odt",
            outputfile=output,
            extra_args=[
                "-M512M -RTS",
                f"--template={tpl_name}",
                f"--reference-doc={ref_name}",
                f"--metadata=lang_name:{contextdict['lang_name']}",
                f"--metadata=title:{contextdict['title']}",
            ],
        )
        result = open(output, "rb").read()

    finally:
        if result and os.path.exists(tmp):
            shutil.rmtree(tmp)

    res = HttpResponse(
        result, content_type="application/vnd.oasis.opendocument.text", charset="utf-8"
    )
    res["content-disposition"] = f'attachment; filename="{filename}"'
    return res
