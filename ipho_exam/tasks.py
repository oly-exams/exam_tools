from __future__ import absolute_import

from django.core.files.base import ContentFile
from celery import shared_task
from ipho_exam import pdf, models
from hashlib import md5
from django.utils import timezone

## utils
def all_same(items):
    return all(x == items[0] for x in items)


## tasks

@shared_task
def compile_tex(body, ext_resources, filename='question.pdf', etag=None):
    if etag is None:
        etag = md5(body).hexdigest()
    doc_pdf = pdf.compile_tex(body, ext_resources)
    meta = {
        'etag': etag,
        'filename': filename,
        'num_pages': pdf.get_num_pages(doc_pdf),
        'barcode_num_pages': 0,
        'barcode_base': None,
    }
    return doc_pdf, meta

@shared_task
def serve_pdfnode(question_pdf, filename='question.pdf'):
    etag = md5(question_pdf).hexdigest()
    meta = {
        'etag': etag,
        'filename': filename,
        'num_pages': pdf.get_num_pages(question_pdf),
        'barcode_num_pages': 0,
        'barcode_base': None,
    }
    return question_pdf, meta

@shared_task
def add_barcode(compiled_pdf, bgenerator):
    question_pdf, meta = compiled_pdf
    doc_pdf = pdf.add_barcode(question_pdf, bgenerator)
    meta['barcode_num_pages'] = meta['num_pages']
    meta['barcode_base'] = bgenerator.base
    return doc_pdf, meta

@shared_task
def concatenate_documents(all_pages, filename='exam.pdf'):
    doc_pdf = pdf.concatenate_documents([question_pdf for question_pdf,_ in all_pages])
    meta = {}
    meta['filename'] = filename
    meta['etag'] = md5(''.join([meta['etag'] for _,meta in all_pages])).hexdigest()
    meta['num_pages'] = sum([meta['num_pages'] for _,meta in all_pages])
    meta['barcode_num_pages'] = sum([meta['barcode_num_pages'] for _,meta in all_pages])
    all_codes = [meta['barcode_base'] for _,meta in all_pages if meta['barcode_base'] is not None]
    if all_same(all_codes):
        meta['barcode_base'] = all_codes[0] if len(all_codes) > 0 else ''
    else:
        meta['barcode_base'] = ','.join(all_codes)
    return doc_pdf, meta

@shared_task(bind=True)
def wait_and_concatenate(self, all_tasks, filename='exam.pdf'):
    for t in all_tasks:
        if not t.ready():
            self.retry(countdown=1)
        elif t.failed():
            raise t.result
    all_pages = [t.result for t in all_tasks]
    doc_pdf = pdf.concatenate_documents([question_pdf for question_pdf,_ in all_pages])

    meta = {}
    meta['filename'] = filename
    meta['etag'] = md5(''.join([meta['etag'] for _,meta in all_pages])).hexdigest()
    meta['num_pages'] = sum([meta['num_pages'] for _,meta in all_pages])
    meta['barcode_num_pages'] = sum([meta['barcode_num_pages'] for _,meta in all_pages])
    all_codes = [meta['barcode_base'] for _,meta in all_pages if meta['barcode_base'] is not None]
    if all_same(all_codes):
        meta['barcode_base'] = all_codes[0] or None
    else:
        meta['barcode_base'] = ','.join(all_codes)
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
        contentfile.name = meta['filename']
        doc.file = contentfile
        doc.num_pages = meta['num_pages']
        doc.barcode_num_pages = meta['barcode_num_pages']
        doc.barcode_base = meta['barcode_base']
        doc.save()
        doc_task.delete()
    except models.DocumentTask.DoesNotExist:
        pass

@shared_task(bind=True)
def identity_args(self, prev_task):
    return prev_task

@shared_task(bind=True)
def student_exam_document(self, questions, student_languages, cover=None, commit=False):
    meta = {}
    meta['num_pages'] = 0
    meta['barcode_num_pages'] = 0
    meta['barcode_base'] = ''
    meta['etag'] = ''
    meta['filename'] = ''
    all_barcodes = []
    all_docs = []
    if cover is not None:
        body = render_to_string('ipho_exam/tex/exam_cover.tex', RequestContext(HttpRequest(), cover)).encode("utf-8")
        question_pdf = pdf.compile_tex(body, [])
        q = questions[0]
        s = student_languages[0].student
        bgenerator = iphocode.QuestionBarcodeGen(q.exam, q, s, qcode='C')
        page = pdf.add_barcode(question_pdf, bgenerator)
        doc_pages = pdf.get_num_pages(page)
        meta['num_pages'] += doc_pages
        meta['barcode_num_pages'] += doc_pages
        all_barcodes.append(bgenerator.base)
        all_docs.append(page)

    for question in questions:
        for sl in student_languages:
            if question.is_answer_sheet() and not sl.with_answer:
                continue

            print 'Prepare', question, 'in', sl.language
            trans = qquery.latest_version(question.pk, sl.language.pk) ## TODO: simplify latest_version, because question and language are already in memory
            if not trans.lang.is_pdf:
                trans_content, ext_resources = trans.qml.make_tex()
                for r in ext_resources:
                    if isinstance(r, tex.FigureExport):
                        r.lang = sl.language
                ext_resources.append(tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls'))
                context = {
                            'polyglossia' : sl.language.polyglossia,
                            'polyglossia_options' : sl.language.polyglossia_options,
                            'font'        : fonts.ipho[sl.language.font],
                            'extraheader' : sl.language.extraheader,
                            'lang_name'   : u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
                            'exam_name'   : u'{}'.format(question.exam.name),
                            'code'        : u'{}{}'.format(question.code, question.position),
                            'title'       : u'{} - {}'.format(question.exam.name, question.name),
                            'is_answer'   : question.is_answer_sheet(),
                            'document'    : trans_content,
                          }
                body = render_to_string('ipho_exam/tex/exam_question.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
                print 'Compile', question, student, sl.language
                question_pdf = pdf.compile_tex(body, ext_resources)
            else:
                question_pdf = trans.node.pdf.read()

            doc_pages = pdf.get_num_pages(question_pdf)
            meta['num_pages'] += doc_pages
            if question.is_answer_sheet():
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student)
                page = pdf.add_barcode(question_pdf, bgenerator)
                meta['barcode_num_pages'] += doc_pages
                all_barcodes.append(bgenerator.base)
                all_docs.append( page )
            else:
                all_docs.append(question_pdf)

            if question.is_answer_sheet() and question.working_pages > 0:
                context = {
                            'polyglossia' : 'english',
                            'polyglossia_options' : '',
                            'font'        : fonts.ipho['notosans'],
                            'extraheader' : '',
                            # 'lang_name'   : u'{} ({})'.format(sl.language.name, sl.language.delegation.country),
                            'exam_name'   : u'{}'.format(question.exam.name),
                            'code'        : u'{}{}'.format('W', question.position),
                            'title'       : u'{} - {}'.format(question.exam.name, question.name),
                            'is_answer'   : question.is_answer_sheet(),
                            'pages'       : range(question.working_pages),
                          }
                body = render_to_string('ipho_exam/tex/exam_blank.tex', RequestContext(HttpRequest(), context)).encode("utf-8")
                question_pdf = pdf.compile_tex(body, [
                    tex.TemplateExport('ipho_exam/tex_resources/ipho2016.cls')
                ])
                bgenerator = iphocode.QuestionBarcodeGen(question.exam, question, sl.student, qcode='W')
                page = pdf.add_barcode(question_pdf, bgenerator)

                doc_pages = pdf.get_num_pages(page)
                meta['num_pages'] += doc_pages
                meta['barcode_num_pages'] += doc_pages
                all_barcodes.append(bgenerator.base)
                all_docs.append(page)

        exam_id = question.exam.pk
        position = question.position

    if all_same(all_barcodes):
        meta['barcode_base'] = all_barcodes[0] or None
    else:
        meta['barcode_base'] = ','.join(all_barcodes)

    filename = u'{}_EXAM-{}-{}.pdf'.format(sl.student.code, exam_id, position)
    final_doc = pdf.concatenate_documents(all_docs)
    meta['filename'] = filename
    meta['etag'] = md5(final_doc).hexdigest()
    if commit:
        try:
            doc_task = models.DocumentTask.objects.get(task_id=self.request.id)
            doc = doc_task.document
            contentfile = ContentFile(doc_pdf)
            contentfile.name = meta['filename']
            doc.file = contentfile
            doc.num_pages = meta['num_pages']
            doc.barcode_num_pages = meta['barcode_num_pages']
            doc.barcode_base = meta['barcode_base']
            doc.save()
            doc_task.delete()
        except models.DocumentTask.DoesNotExist:
            pass


    return final_doc, meta


@shared_task(bind=True)
def cleanup_meta(self):
    from djcelery.models import TaskMeta
    TaskMeta.objects.filter(date_done__lte=timezone.now() - timezone.timedelta(minutes=25)).delete()
