from __future__ import absolute_import

from celery import shared_task
from ipho_exam import pdf

@shared_task
def compile_tex(body, ext_resources, filename='question.pdf', etag=None):
    return filename, pdf.compile_tex(body, ext_resources), etag

@shared_task
def add_barcode(compiled_pdf, bgenerator):
    filename, question_pdf, etag = compiled_pdf
    return filename, pdf.add_barcode(question_pdf, bgenerator), etag

def print_structure(sets):
    res = 'size={} :: '.format(len(sets))
    for ss in sets:
        if isinstance(ss, list):
            res += '[{}], '.format(print_structure(ss))
        elif isinstance(ss, tuple):
            res += '({}), '.format(print_structure(ss))
        else:
            res += '{}, '.format(type(ss))
    return res

@shared_task
def concatenate_documents(all_pages, filename='exam.pdf'):
    return filename, pdf.concatenate_documents([question_pdf for filename, question_pdf, etag in all_pages]), None
