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

from django.http import HttpResponse
from django.conf import settings

from appy.pod.renderer import Renderer as ODTRenderer

from . import tex

TEMPLATE_PATH = getattr(settings, "TEMPLATE_PATH")
TEMP_PREFIX = getattr(settings, "ODT_TEMP_PREFIX", "render_odt-")

logger = logging.getLogger("ipho_exam")


def render_odt_response(tpl_name, context, filename, ext_resources):
    origin = os.path.join(TEMPLATE_PATH, tpl_name)
    contextdict = {}
    for data in context:
        contextdict.update(**data)
    result = None
    output = None
    try:
        tmp = mkdtemp(prefix=TEMP_PREFIX)

        for res in ext_resources:
            res.save(tmp)
            if isinstance(res, tex.FigureExport):
                contextdict["document"] = contextdict["document"].replace(
                    res.figname, f"{tmp}/{res.figname}"
                )

        output = f"{tmp}/doc.odt"
        logger.debug(
            "Render template '%s' to '%s'", tpl_name, output
        )  # this is recommended by pylint W1201
        renderer = ODTRenderer(origin, contextdict, output, overwriteExisting=True)
        renderer.run()
        result = open(output, "rb").read()
    # except (OSError, PodError), e:
    #     logger.error("Cannot render '{}' : {}" % (tpl_name, e))
    #     raise e
    finally:
        if output and os.path.exists(tmp):
            shutil.rmtree(tmp)

    res = HttpResponse(
        result, content_type="application/vnd.oasis.opendocument.text", charset="utf-8"
    )
    res["content-disposition"] = f'attachment; filename="{filename}"'
    return res
