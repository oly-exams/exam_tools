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

from __future__ import print_function
from __future__ import division

import codecs
from builtins import range
from past.utils import old_div
from django.http import HttpResponse, Http404, HttpResponseNotModified
from django.core.cache import cache
from django.conf import settings

from tempfile import mkdtemp
import subprocess
import os
import shutil
from hashlib import md5

from PyPDF2 import PdfFileWriter, PdfFileReader
from io import StringIO, BytesIO

TEMP_PREFIX = getattr(settings, 'TEX_TEMP_PREFIX', 'render_tex-')
CACHE_PREFIX = getattr(settings, 'TEX_CACHE_PREFIX', 'render-tex')
CACHE_TIMEOUT = getattr(settings, 'TEX_CACHE_TIMEOUT', 300)  # 1 min
TEXBIN = getattr(settings, 'TEXBIN', '/usr/bin')


class TexCompileException(Exception):
    def __init__(self, code, doc_fname='', log='', doc_tex=''):
        self.log = log
        self.code = code
        self.doc_fname = doc_fname
        self.doc_tex = doc_tex
        super(TexCompileException, self).__init__("pdflatex error (code %s) in %s, log:\n %s." % (code, doc_fname, log))


def compile_tex(body, ext_resources=[]):
    doc = 'question'
    etag = md5(body.encode('utf8')).hexdigest()

    cache_key = "%s:%s" % (CACHE_PREFIX, etag)
    pdf = cache.get(cache_key)
    if pdf is None:
        if '\\nonstopmode' not in body:
            raise ValueError("\\nonstopmode not present in document, cowardly refusing to process.")

        tmp = mkdtemp(prefix=TEMP_PREFIX)
        try:
            for res in ext_resources:
                res.save(tmp)

            with codecs.open("%s/%s.tex" % (tmp, doc), "w", encoding='utf-8') as f:
                f.write(body)

            error = subprocess.Popen(
                ["xelatex", "%s.tex" % doc],
                cwd=tmp,
                env={
                    'PATH': '{}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'.format(TEXBIN)
                },
                stdin=open(os.devnull, "r"),
                stderr=open(os.devnull, "wb"),
                stdout=open(os.devnull, "wb")
            ).wait()

            if error:
                if not os.path.exists("%s/%s.log" % (tmp, doc)):
                    raise RuntimeError('Error in PDF. Errocode {}. Log does not exists.'.format(error))
                log = open("%s/%s.log" % (tmp, doc), errors='replace').read()
                raise TexCompileException(error, "%s/%s.tex" % (tmp, doc), log, doc_tex=body)

            del body

            with open("%s/%s.pdf" % (tmp, doc), 'rb') as f:
                pdf = f.read()
        finally:
            # print('Compiled in', tmp)
            shutil.rmtree(tmp)

        if pdf:
            cache.set(cache_key, pdf, CACHE_TIMEOUT)
    return pdf


def add_barcode(doc, bgenerator):
    pdfdoc = PdfFileReader(BytesIO(doc))

    output = PdfFileWriter()
    for i in range(pdfdoc.getNumPages()):
        barpdf = PdfFileReader(BytesIO(bgenerator(i + 1)))
        watermark = barpdf.getPage(0)
        wbox = watermark.artBox
        wwidth = (wbox.upperRight[0] - wbox.upperLeft[0])

        page = pdfdoc.getPage(i)
        pbox = page.artBox
        pwidth = (pbox.upperRight[0] - pbox.upperLeft[0])

        scale = 1.5  # size of the QR code (scaling factor)
        yshift = 70  # distance from page top
        x = float(pbox.upperLeft[0]) + old_div((float(pwidth) - float(wwidth) * scale), 2.)
        y = float(pbox.upperLeft[1]) - float(wbox.upperLeft[1]) - yshift

        page.mergeScaledTranslatedPage(watermark, scale, x, y)
        output.addPage(page)

    output_pdf = BytesIO()
    output.write(output_pdf)
    return output_pdf.getvalue()


def get_num_pages(doc):
    pdfdoc = PdfFileReader(BytesIO(doc))
    return pdfdoc.getNumPages()


def concatenate_documents(all_documents):
    output = PdfFileWriter()
    for doc in all_documents:
        pdfdoc = PdfFileReader(BytesIO(doc))
        for i in range(pdfdoc.getNumPages()):
            output.addPage(pdfdoc.getPage(i))
    output_pdf = BytesIO()
    output.write(output_pdf)
    return output_pdf.getvalue()


def cached_pdf_response(request, body, ext_resources=[], filename='question.pdf'):
    etag = md5(body.encode('utf8')).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()

    try:
        # print('Trying to spawn task')
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
    res['content-disposition'] = 'inline; filename="{}"'.format(filename)
    res['ETag'] = etag
    return res
