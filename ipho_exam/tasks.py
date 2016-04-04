from __future__ import absolute_import

from celery import shared_task
from ipho_exam import pdf

@shared_task
def compile_tex(body, ext_resources, filename='question.pdf', etag=None):
    return filename, pdf.compile_tex(body, ext_resources), etag
