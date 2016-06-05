from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, JsonResponse, Http404, HttpResponseForbidden
try:
    from django.template.loader import find_template
except:
    from django.template import engines
    find_template = engines['django'].engine.find_template
from django.conf import settings

from appy.pod.renderer import Renderer as ODTRenderer
from appy.pod import PodError

import os
import logging
from tempfile import NamedTemporaryFile

TEMPLATE_PATH = getattr(settings, 'TEMPLATE_PATH')

logger = logging.getLogger('ipho_exam')

def render_odt_response(tpl_name, context, filename):
    origin = os.path.join(TEMPLATE_PATH,tpl_name)
    contextdict = {}
    for d in context: contextdict.update(**d)
    result = None
    output = None
    try:
        with NamedTemporaryFile('wb', suffix='.odt', delete=False) as f:
            output = f.name
        logger.debug("Render template '%s' to '%s'" % (tpl_name, output))
        renderer = ODTRenderer(origin, contextdict, output, overwriteExisting=True)
        renderer.run()
        result = open(output, 'rb').read()
    # except (OSError, PodError), e:
    #     logger.error("Cannot render '%s' : %s" % (tpl_name, e))
    #     raise e
    finally:
        if output and os.path.exists(output):
            os.unlink(output)

    res = HttpResponse(result, content_type="application/vnd.oasis.opendocument.text", charset="utf-8")
    res['content-disposition'] = 'attachment; filename="{}"'.format(filename.encode('utf-8'))
    return res