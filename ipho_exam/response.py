# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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

from __future__ import absolute_import

import os, shutil
import logging
from tempfile import mkdtemp

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, JsonResponse, Http404, HttpResponseForbidden
try:
    from django.template.loader import find_template
except:
    from django.template import engines
    find_template = engines['django'].engine.find_template
from django.conf import settings

from appy.pod.renderer import Renderer as ODTRenderer

from . import tex

TEMPLATE_PATH = getattr(settings, 'TEMPLATE_PATH')
TEMP_PREFIX = getattr(settings, 'ODT_TEMP_PREFIX', 'render_odt-')

logger = logging.getLogger('ipho_exam')

def render_odt_response(tpl_name, context, filename, ext_resources):
    origin = os.path.join(TEMPLATE_PATH,tpl_name)
    contextdict = {}
    for d in context: contextdict.update(**d)
    result = None
    output = None
    try:
        tmp = mkdtemp(prefix=TEMP_PREFIX)

        for res in ext_resources:
            res.save(tmp)
            if isinstance(res, tex.FigureExport):
                contextdict['document'] = contextdict['document'].replace(res.figname, "%s/%s" % (tmp, res.figname))

        output = "%s/%s.odt" % (tmp, 'doc')
        logger.debug("Render template '%s' to '%s'" % (tpl_name, output))
        renderer = ODTRenderer(origin, contextdict, output, overwriteExisting=True)
        renderer.run()
        result = open(output, 'rb').read()
    # except (OSError, PodError), e:
    #     logger.error("Cannot render '%s' : %s" % (tpl_name, e))
    #     raise e
    finally:
        if output and os.path.exists(tmp):
            shutil.rmtree(tmp)

    res = HttpResponse(result, content_type="application/vnd.oasis.opendocument.text", charset="utf-8")
    res['content-disposition'] = 'attachment; filename="{}"'.format(filename.encode('utf-8'))
    return res
