from __future__ import absolute_import

from celery import shared_task
from ipho_exam import pdf
from hashlib import md5

@shared_task
def compile_tex(body, ext_resources, filename='question.pdf', etag=None):
    if etag is None:
        etag = md5(body).hexdigest()
    return filename, pdf.compile_tex(body, ext_resources), etag

@shared_task
def add_barcode(compiled_pdf, bgenerator):
    filename, question_pdf, etag = compiled_pdf
    return filename, pdf.add_barcode(question_pdf, bgenerator), etag

@shared_task
def concatenate_documents(all_pages, filename='exam.pdf'):
    etag = md5(''.join([etag for filename, question_pdf, etag in all_pages])).hexdigest()
    return filename, pdf.concatenate_documents([question_pdf for filename, question_pdf, etag in all_pages]), etag