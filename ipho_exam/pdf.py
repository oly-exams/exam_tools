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
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 300)  # 1 min
TEXBIN = getattr(settings, 'TEXBIN', '/usr/bin')


class TexCompileException(Exception):
    def __init__(self, code, doc_fname='', log=''):
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
                env={'PATH':'{}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'.format(TEXBIN)},
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()

            if error:
                if not os.path.exists("%s/%s.log" % (tmp, doc)):
                    raise RuntimeError('Error in PDF. Errocode {}. Log does not exists.'.format(error))
                log = open("%s/%s.log" % (tmp, doc)).read()
                raise TexCompileException(error, "%s/%s"%(tmp, doc), log)

            with open("%s/%s.pdf" % (tmp, doc)) as f:
                pdf = f.read()
        finally:
            # print 'Compiled in', tmp
            shutil.rmtree(tmp)

        if pdf:
            cache.set(cache_key, pdf, CACHE_TIMEOUT)
    return pdf

def add_barcode(doc, bgenerator):
    pdfdoc = PdfFileReader(StringIO(doc))

    output = PdfFileWriter()
    for i in xrange(pdfdoc.getNumPages()):
        barpdf = PdfFileReader(StringIO(bgenerator(i+1)))
        watermark = barpdf.getPage(0)
        wbox = watermark.artBox
        wwidth = (wbox.upperRight[0] - wbox.upperLeft[0])

        page = pdfdoc.getPage(i)
        pbox = page.artBox
        pwidth = (pbox.upperRight[0] - pbox.upperLeft[0])

        scale = 1.66
        yshift = 83
        x = float(pbox.upperLeft[0]) + (float(pwidth) - float(wwidth)*scale) / 2.
        y = float(pbox.upperLeft[1]) -  float(wbox.upperLeft[1]) - yshift

        page.mergeScaledTranslatedPage(watermark, scale, x, y)
        output.addPage(page)

    output_pdf = StringIO()
    output.write(output_pdf)
    return output_pdf.getvalue()

def get_num_pages(doc):
    pdfdoc = PdfFileReader(StringIO(doc))
    return pdfdoc.getNumPages()

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

    try:
        # print 'Trying to spawn task'
        # job = tasks.compile_tex.delay(body, ext_resources)
        # if not job.ready():
        #     return HttpResponse('Computing...')
        # pdf = job.get()
        #
        pdf = compile_tex(body, ext_resources)
    except TexCompileException as e:
        if request.user.is_superuser:
            return HttpResponse(e.log, content_type="text/plain")
        else:
            raise RuntimeError("pdflatex error (code %s) in %s." % (e.code, e.doc_fname))

    res = HttpResponse(pdf, content_type="application/pdf")
    res['content-disposition'] = 'inline; filename="{}"'.format(filename.encode('utf-8'))
    res['ETag'] = etag
    return res
