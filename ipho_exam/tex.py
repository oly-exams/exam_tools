from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5

from ipho_exam.models import Figure


TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 60)  # 1 min


def html2tex(el):
    result = []
    if el.text:
        result.append(el.text)
    for sel in el:
        ## Span styling
        if sel.tag in ["span"]:
            for att in sel.attrib.keys():
                if att =='style':
                    if 'font-style:italic' in sel.attrib[att]:
                        result.append(u'\\textit{%s}' % (html2tex(sel)))
                    elif 'font-weight:bold' in sel.attrib[att]:
                        result.append(u'\\textbf{%s}' % (html2tex(sel)))
                elif att =='class' and 'math-tex' in sel.attrib[att]:
                        result.append( html2tex(sel) )
        ## Bold
        elif sel.tag in ["b","strong"]:
            result.append(u'\\textbf{%s}' % (html2tex(sel)))
        ## Italic
        elif sel.tag in ["i"]:
            result.append(u'\\textit{%s}' % (html2tex(sel)))
        ## Emph
        elif sel.tag in ["em"]:
            result.append(u'\\emph{%s}' % (html2tex(sel)))
        ## Underline
        elif sel.tag in ["u"]:
            result.append(u'\\underline{%s}' % (html2tex(sel)))
        
        ## By default just append content
        else:
            result.append(html2tex(sel))
        if sel.tail:
            result.append(sel.tail)
    return u"".join(result)


class FigureExport(object):
    def __init__(self, figname, figid, query):
        self.figname = figname
        self.figid = figid
        self.query = query
    def save(self, dirname):
        fig_svg = Figure.get_fig_query(self.figid, self.query)
        import cairosvg
        with open('%s/%s' % (dirname, self.figname), 'w') as fp:
            fig_pdf = cairosvg.svg2pdf(fig_svg.encode('utf8'))
            fp.write(fig_pdf)
#        cairosvg.svg2pdf(fig_svg.encode('utf8'), '%s/%s' % (dirname, self.figname))

class StaticExport(object):
    def __init__(self):
        pass
    def save(self, dirname):
        pass

def render_tex(request, template, ctx={}, ext_resources=[]):
    doc = template.rsplit('/', 1)[-1].rsplit('.', 1)[0]
 
    try:
        body = get_template(template).render(Context(ctx)).encode("utf-8")
    except TemplateDoesNotExist:
        raise Http404()
 
    etag = md5(body).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()
 
    cache_key = "%s:%s:%s" % (CACHE_PREFIX, template, etag)
    pdf = cache.get(cache_key)
    if pdf is None:
        if '\\nonstopmode' not in body:
            raise ValueError("\\nonstopmode not present in document, cowardly refusing to process.")
 
        tmp = mkdtemp(prefix=TEMP_PREFIX)
        try:
            for res in ext_resources:
                res.save(tmp)

            with open("%s/%s.tex" % (tmp, doc), "w") as f:
                f.write(body)
            del body
 
            error = subprocess.Popen(
                ["xelatex", "%s.tex" % doc],
                cwd=tmp,
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()
 
            if error:
                if request.user.is_superuser:
                    log = open("%s/%s.log" % (tmp, doc)).read()
                    return HttpResponse(log, content_type="text/plain")
                else:
                    raise RuntimeError("pdflatex error (code %s) in %s/%s" % (error, tmp, doc))
 
            pdf = open("%s/%s.pdf" % (tmp, doc))
        finally:
            shutil.rmtree(tmp)
 
        if pdf:
            cache.set(cache_key, pdf, CACHE_TIMEOUT)
 
    res = HttpResponse(pdf, content_type="application/pdf")
    res['content-disposition'] = 'inline; filename="{}"'.format(ctx['filename'])
    res['ETag'] = etag
    return res
