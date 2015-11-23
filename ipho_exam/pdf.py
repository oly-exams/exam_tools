from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5

from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO

TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 60)  # 1 min


class TexCompileException(Exception):
    def __init__(self, code, doc_fname, log):
        self.log = log
        self.code = code
        self.doc_fname = doc_fname
        super(TexCompileException, self).__init__("pdflatex error (code %s) in %s" % (code, doc_fname))


def compile_tex(body, ext_resources=[]):
    doc = 'question'
    etag = md5(body).hexdigest()

    cache_key = "%s:%s" % (CACHE_PREFIX, etag)
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
                    raise TexCompileException(error, "%s/%s"%(tmp, doc), log)
                    # return HttpResponse(log, content_type="text/plain")
                else:
                    raise RuntimeError("pdflatex error (code %s) in %s/%s" % (error, tmp, doc))

            with open("%s/%s.pdf" % (tmp, doc)) as f:
                pdf = f.read()
        finally:
            shutil.rmtree(tmp)

        if pdf:
            cache.set(cache_key, pdf, CACHE_TIMEOUT)
    return pdf

def concatenate_documents(all_documents):
    output = PdfFileWriter()
    for doc in  all_documents:
        pdfdoc = PdfFileReader(StringIO(doc))
        for i in xrange(pdfdoc.getNumPages()):
            output.addPage(pdfdoc.getPage(i))
    output_pdf = StringIO()
    output.write(output_pdf)
    return output_pdf.getvalue()

def cached_pdf_response(request, body, ext_resources=[], filename='question.pdf'):
    etag = md5(body).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()

    pdf = compile_tex(body, ext_resources)

    res = HttpResponse(pdf, content_type="application/pdf")
    res['content-disposition'] = 'inline; filename="{}"'.format(filename.encode('utf-8'))
    res['ETag'] = etag
    return res
