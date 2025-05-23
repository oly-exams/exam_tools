import codecs
import logging
import os
import shutil
import subprocess
from hashlib import md5
from io import BytesIO
from pathlib import Path
from tempfile import mkdtemp

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotModified
from PyPDF2 import PdfFileReader, PdfFileWriter

TEMP_PREFIX = getattr(settings, "TEX_TEMP_PREFIX", "render_tex-")
CACHE_PREFIX = getattr(settings, "TEX_CACHE_PREFIX", "render-tex")
CACHE_TIMEOUT = getattr(settings, "TEX_CACHE_TIMEOUT", 600)  # 10 min
TEXBIN = getattr(settings, "TEXBIN", "/usr/bin")
WATERMARK_PATH = getattr(
    settings, "WATERMARK_PATH", os.path.join(settings.STATIC_PATH, "watermark.pdf")
)

# Get an instance of a logger
logger = logging.getLogger("ipho_exam.pdf")


class TexCompileException(Exception):
    def __init__(self, code, doc_fname="", log="", doc_tex=""):
        self.log = log
        self.code = code
        self.doc_fname = doc_fname
        self.doc_tex = doc_tex
        super().__init__(f"pdflatex error (code {code}) in {doc_fname}, log:\n {log}.")


def compile_tex_diff(old_body, new_body, ext_resources=tuple()):
    tmpdir = mkdtemp(prefix=TEMP_PREFIX)
    try:
        with codecs.open(os.path.join(tmpdir, "new.tex"), "w", encoding="utf-8") as f:
            f.write(new_body)
        with codecs.open(os.path.join(tmpdir, "old.tex"), "w", encoding="utf-8") as f:
            f.write(old_body)
        diff_body = subprocess.check_output(
            ["latexdiff", "--encoding=utf-8", "old.tex", "new.tex"],
            cwd=tmpdir,
            env={
                "PATH": f"{TEXBIN}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            },
        ).decode("utf-8")
    finally:
        shutil.rmtree(tmpdir)
    return compile_tex(diff_body, ext_resources=ext_resources)


def compile_tex(body, ext_resources=tuple()):
    doc = "question"
    etag = md5(body.encode("utf8")).hexdigest()
    # pylint: disable=consider-using-with
    cache_key = f"{CACHE_PREFIX}:{etag}"
    pdf = cache.get(cache_key)
    # body = body.replace("&#39;", "'") # convert HTML apostrophe in human readable apostrophe
    if pdf is None:
        logger.debug("Hash of tex not found in cache")
        if "\\nonstopmode" not in body:
            raise ValueError(
                "\\nonstopmode not present in document, cowardly refusing to process."
            )

        tmp = mkdtemp(prefix=TEMP_PREFIX)
        try:
            for res in ext_resources:
                res.save(tmp)

            with codecs.open(f"{tmp}/{doc}.tex", "w", encoding="utf-8") as f:
                f.write(body)

            env = {
                "PATH": f"{TEXBIN}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            }
            event_packages = Path(settings.EVENT_TEMPLATE_PATH) / "tex_packages"
            if event_packages.exists():
                env["TEXINPUTS"] = f".:{event_packages}:"

            error = subprocess.Popen(
                ["xelatex", f"{doc}.tex"],
                cwd=tmp,
                env=env,
                stdin=open(os.devnull, encoding="utf-8"),
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            ).wait()

            if error:
                if not os.path.exists(f"{tmp}/{doc}.log"):
                    raise RuntimeError(
                        f"Error in PDF. Errocode {error}. Log does not exists."
                    )
                log = open(
                    f"{tmp}/{doc}.log", errors="replace", encoding="utf-8"
                ).read()
                raise TexCompileException(error, f"{tmp}/{doc}.tex", log, doc_tex=body)

            del body

            with open(f"{tmp}/{doc}.pdf", "rb") as f:
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
        wwidth = wbox.getWidth()

        page = pdfdoc.getPage(i)
        pbox = page.artBox
        pwidth = pbox.getWidth()

        scale = 1.5  # size of the QR code (scaling factor)
        yshift = 20  # distance from page top
        x = float(pbox.getUpperLeft_x()) + (float(pwidth) - float(wwidth) * scale) / 2
        y = float(pbox.getUpperLeft_y()) - float(wbox.getHeight()) * scale - yshift

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


def cached_pdf_response(request, body, ext_resources=tuple(), filename="question.pdf"):
    etag = md5(body.encode("utf8")).hexdigest()
    if request.META.get("HTTP_IF_NONE_MATCH", "") == etag:
        return HttpResponseNotModified()

    try:
        # print('Trying to spawn task')
        # job = tasks.compile_tex.delay(body, ext_resources)
        # if not job.ready():
        #     return HttpResponse('Computing...')
        # pdf = job.get()
        #
        pdf = compile_tex(body, ext_resources)
    except TexCompileException as err:
        if request.user.is_superuser:
            return HttpResponse(err.log, content_type="text/plain")

        raise RuntimeError(
            f"pdflatex error (code {err.code}) in {err.doc_fname}."
        ) from err

    output_pdf = check_add_watermark(request, pdf)
    res = HttpResponse(output_pdf, content_type="application/pdf")
    res["content-disposition"] = f'inline; filename="{filename}"'
    res["ETag"] = etag
    return res


def check_add_watermark(request, doc):
    """
    Checks if the 'delegation print' watermark needs to be added to the document,
    and return the appropriate PDF (with / without watermark).
    """
    if settings.ADD_DELEGATION_WATERMARK:
        user = request.user
        if not (
            user.is_staff
            or user.has_perm("ipho_core.is_organizer_admin")
            or user.has_perm("ipho_core.can_edit_exam")
            or user.has_perm("ipho_core.is_printstaff")
            or user.has_perm("ipho_core.is_marker")
            or user.has_perm(
                "ipho_core.is_delegation_print"
            )  # do not print watermark on prints by delegation examsite team
        ):
            return add_watermark(doc)
    return doc


def add_watermark(doc, watermark_filename=None):
    """
    Adds the 'delegation print' watermark to the given PDF document.
    """
    filename = WATERMARK_PATH
    if watermark_filename:
        filename = Path(filename).parent / watermark_filename

    with open(filename, "rb") as wm_f:
        watermark = PdfFileReader(BytesIO(wm_f.read()))
        watermark_page = watermark.getPage(0)

    output = PdfFileWriter()
    pdfdoc = PdfFileReader(BytesIO(doc))
    for idx in range(pdfdoc.getNumPages()):
        page = pdfdoc.getPage(idx)
        page.mergePage(watermark_page)
        output.addPage(page)

    output_pdf = BytesIO()
    output.write(output_pdf)
    return output_pdf.getvalue()
