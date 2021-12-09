# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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


from hashlib import md5
from celery import shared_task

from django_celery_results.models import TaskResult
from django.core.files.base import ContentFile
from django.utils import timezone

from ipho_exam import pdf, compile_utils, models


## utils
def all_same(items):
    return all(x == items[0] for x in items)


## tasks


@shared_task
def compile_tex(body, ext_resources, filename="question.pdf", etag=None):
    if etag is None:
        etag = md5(body.encode("utf8")).hexdigest()
    doc_pdf = pdf.compile_tex(body, ext_resources)
    meta = {
        "etag": etag,
        "filename": filename,
        "num_pages": pdf.get_num_pages(doc_pdf),
        "barcode_num_pages": 0,
        "barcode_base": None,
    }
    return doc_pdf, meta


@shared_task
def compile_tex_diff(
    old_body, new_body, ext_resources, filename="question.pdf", etag=None
):
    if etag is None:
        etag = md5((old_body + new_body).encode("utf8")).hexdigest()
    doc_pdf = pdf.compile_tex_diff(old_body, new_body, ext_resources)
    meta = {
        "etag": etag,
        "filename": filename,
        "num_pages": pdf.get_num_pages(doc_pdf),
        "barcode_num_pages": 0,
        "barcode_base": None,
    }
    return doc_pdf, meta


@shared_task
def serve_pdfnode(question_pdf, filename="question.pdf"):
    etag = md5(question_pdf).hexdigest()
    meta = {
        "etag": etag,
        "filename": filename,
        "num_pages": pdf.get_num_pages(question_pdf),
        "barcode_num_pages": 0,
        "barcode_base": None,
    }
    return question_pdf, meta


@shared_task
def add_barcode(compiled_pdf, bgenerator):
    question_pdf, meta = compiled_pdf
    doc_pdf = pdf.add_barcode(question_pdf, bgenerator)
    meta["barcode_num_pages"] = meta["num_pages"]
    meta["barcode_base"] = bgenerator.base
    return doc_pdf, meta


@shared_task
def concatenate_documents(all_pages, filename="exam.pdf"):
    doc_pdf = pdf.concatenate_documents([question_pdf for question_pdf, _ in all_pages])
    meta = {}
    meta["filename"] = filename
    meta["etag"] = md5(
        ("".join([meta["etag"] for _, meta in all_pages])).encode("utf8")
    ).hexdigest()
    meta["num_pages"] = sum([meta["num_pages"] for _, meta in all_pages])
    meta["barcode_num_pages"] = sum(
        [meta["barcode_num_pages"] for _, meta in all_pages]
    )
    all_codes = [
        meta["barcode_base"]
        for _, meta in all_pages
        if meta["barcode_base"] is not None
    ]
    if all_same(all_codes):
        meta["barcode_base"] = all_codes[0] if len(all_codes) > 0 else ""
    else:
        meta["barcode_base"] = ",".join(all_codes)
    return doc_pdf, meta


@shared_task(bind=True)
def wait_and_concatenate(self, all_tasks, filename="exam.pdf"):
    for t in all_tasks:
        if not t.ready():
            self.retry(countdown=1)
        elif t.failed():
            raise t.result
    all_pages = [t.result for t in all_tasks]
    doc_pdf = pdf.concatenate_documents([question_pdf for question_pdf, _ in all_pages])

    meta = {}
    meta["filename"] = filename
    meta["etag"] = md5(
        ("".join([meta["etag"] for _, meta in all_pages])).encode("utf8")
    ).hexdigest()
    meta["num_pages"] = sum([meta["num_pages"] for _, meta in all_pages])
    meta["barcode_num_pages"] = sum(
        [meta["barcode_num_pages"] for _, meta in all_pages]
    )
    all_codes = [
        meta["barcode_base"]
        for _, meta in all_pages
        if meta["barcode_base"] is not None
    ]
    if all_same(all_codes):
        meta["barcode_base"] = all_codes[0] or None
    else:
        meta["barcode_base"] = ",".join(all_codes)
    return doc_pdf, meta


@shared_task(bind=True)
def commit_compiled_exam(self, compile_job):
    if len(compile_job) == 1 and len(compile_job[0]) == 3:
        compile_job = compile_job[0]
    doc_pdf, meta = compile_job
    try:
        doc_task = models.DocumentTask.objects.get(task_id=self.request.id)
        doc = doc_task.document
        contentfile = ContentFile(doc_pdf)
        contentfile.name = meta["filename"]
        doc.file = contentfile
        doc.num_pages = meta["num_pages"]
        doc.barcode_num_pages = meta["barcode_num_pages"]
        doc.barcode_base = meta["barcode_base"]
        doc.save()
        doc_task.delete()
    except models.DocumentTask.DoesNotExist:
        pass


@shared_task(bind=True)
def identity_args(self, prev_task):  # pylint: disable=unused-argument
    return prev_task


@shared_task(bind=True)
def participant_exam_document(
    self, questions, participant_languages, cover=None, commit=False,
    question_lang_list=None, answer_lang_list=None
):
    job_task = self.request.id if commit else None
    return compile_utils.participant_exam_document(
        questions, participant_languages, cover, job_task=job_task,
        question_lang_list=question_lang_list, answer_lang_list=answer_lang_list
    )


@shared_task(bind=True)
def cleanup_meta(self):  # pylint: disable=unused-argument
    TaskResult.objects.filter(
        date_done__lte=timezone.now() - timezone.timedelta(minutes=25)
    ).delete()
