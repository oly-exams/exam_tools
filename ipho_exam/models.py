# -*- coding: utf-8 -*-

# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from __future__ import print_function, unicode_literals, absolute_import

import os, uuid
import subprocess

from builtins import object
from builtins import str

from django.db import models
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from ipho_core.models import Delegation, Student
from django.shortcuts import get_object_or_404
from ipho_exam import fonts
from .exceptions import IphoExamException, IphoExamForbidden
from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager

from .utils import natural_id

OFFICIAL_DELEGATION = getattr(settings, 'OFFICIAL_DELEGATION')
SITE_URL = getattr(settings, 'SITE_URL')
INKSCAPE_BIN = getattr(settings, 'INKSCAPE_BIN', 'inkscape')


class LanguageManager(models.Manager):
    def get_by_natural_key(self, name, delegation_name):
        return self.get(name=name, delegation=Delegation.objects.get_by_natural_key(delegation_name))


@python_2_unicode_compatible
class Language(models.Model):
    objects = LanguageManager()
    DIRECTION_CHOICES = (('ltr', 'Left-to-right'), ('rtl', 'Right-to-left'))
    POLYGLOSSIA_CHOICES = (('albanian', 'Albanian'), ('amharic', 'Amharic'), ('arabic', 'Arabic'), ('armenian', 'Armenian'), ('asturian', 'Asturian'), ('bahasai', 'Bahasai'), ('bahasam', 'Bahasam'), ('basque', 'Basque'), ('bengali', 'Bengali'), ('brazilian', 'Brazilian'), ('breton', 'Breton'), ('bulgarian', 'Bulgarian'), ('catalan', 'Catalan'), ('coptic', 'Coptic'), ('croatian', 'Croatian'), ('czech', 'Czech'), ('danish', 'Danish'), ('divehi', 'Divehi'), ('dutch', 'Dutch'), ('english', 'English'), ('esperanto', 'Esperanto'), ('estonian', 'Estonian'), ('farsi', 'Farsi'), ('finnish', 'Finnish'), ('french', 'French'), ('friulan', 'Friulan'), ('galician', 'Galician'), ('german', 'German'), ('greek', 'Greek'), ('hebrew', 'Hebrew'), ('hindi', 'Hindi'), ('icelandic', 'Icelandic'), ('interlingua', 'Interlingua'), ('irish', 'Irish'), ('italian', 'Italian'), ('kannada', 'Kannada'), ('lao', 'Lao'), ('latin', 'Latin'), ('latvian', 'Latvian'), ('lithuanian', 'Lithuanian'), ('lsorbian', 'Lsorbian'), ('magyar', 'Magyar'), ('malayalam', 'Malayalam'), ('marathi', 'Marathi'), ('nko', 'Nko'), ('norsk', 'Norsk'), ('nynorsk', 'Nynorsk'), ('occitan', 'Occitan'), ('piedmontese', 'Piedmontese'), ('polish', 'Polish'), ('portuges', 'Portuges'), ('romanian', 'Romanian'), ('romansh', 'Romansh'), ('russian', 'Russian'), ('samin', 'Samin'), ('sanskrit', 'Sanskrit'), ('scottish', 'Scottish'), ('serbian', 'Serbian'), ('slovak', 'Slovak'), ('slovenian', 'Slovenian'), ('spanish', 'Spanish'), ('swedish', 'Swedish'), ('syriac', 'Syriac'), ('tamil', 'Tamil'), ('telugu', 'Telugu'), ('thai', 'Thai'), ('tibetan', 'Tibetan'), ('turkish', 'Turkish'), ('turkmen', 'Turkmen'), ('ukrainian', 'Ukrainian'), ('urdu', 'Urdu'), ('usorbian', 'Usorbian'), ('vietnamese', 'Vietnamese'), ('welsh', 'Welsh'), ('custom', 'Other')) # yapf:disable
    STYLES_CHOICES = ((u'afrikaans', u'Afrikaans'), (u'albanian', u'Albanian'), (u'amharic', u'Amharic'), (u'arabic', u'Arabic'), (u'armenian', u'Armenian'), (u'asturian', u'Asturian'), (u'azerbaijani', u'Azerbaijani'), (u'basque', u'Basque'), (u'belarusian', u'Belarusian'), (u'bengali', u'Bengali'), (u'bosnian', u'Bosnian'), (u'breton', u'Breton'), (u'bulgarian', u'Bulgarian'), (u'burmese', u'Burmese'), (u'cantonese', u'Cantonese'), (u'catalan', u'Catalan'), (u'chinese', u'Chinese'), (u'coptic', u'Coptic'), (u'croatian', u'Croatian'), (u'czech', u'Czech'), (u'danish', u'Danish'), (u'divehi', u'Divehi'), (u'dutch', u'Dutch'), (u'english', u'English'), (u'esperanto', u'Esperanto'), (u'filipino', u'Filipino'), (u'finnish', u'Finnish'), (u'french', u'French'), (u'friulian', u'Friulian'), (u'galician', u'Galician'), (u'georgian', u'Georgian'), (u'german', u'German'), (u'greek', u'Greek'), (u'hebrew', u'Hebrew'), (u'hindi', u'Hindi'), (u'hungarian', u'Hungarian'), (u'icelandic', u'Icelandic'), (u'indonesian', u'Indonesian'), (u'interlingua', u'Interlingua'), (u'irish', u'Irish'), (u'italian', u'Italian'), (u'japanese', u'Japanese'), (u'kannada', u'Kannada'), (u'kazakh', u'Kazakh'), (u'khmer', u'Khmer'), (u'korean', u'Korean'), (u'kurdish', u'Kurdish'), (u'kyrgyz', u'Kyrgyz'), (u'lao', u'Lao'), (u'latin', u'Latin'), (u'latvian', u'Latvian'), (u'lithuanian', u'Lithuanian'), (u'luxembourgish', u'Luxembourgish'), (u'macedonian', u'Macedonian'), (u'magyar', u'Magyar'), (u'malay', u'Malay'), (u'malayalam', u'Malayalam'), (u'malaysian', u'Malaysian'), (u'mandarin', u'Mandarin'), (u'marathi', u'Marathi'), (u'mongolian', u'Mongolian'), (u'montenegrin', u'Montenegrin'), (u'nepali', u'Nepali'), (u'northern sotho', u'Northern Sotho'), (u'norwegian bokmål', u'Norwegian Bokmål'), (u'norwegian nynorsk', u'Norwegian Nynorsk'), (u'occitan', u'Occitan'), (u'persian', u'Persian'), (u'piedmontese', u'Piedmontese'), (u'polish', u'Polish'), (u'portuguese', u'Portuguese'), (u'romanian', u'Romanian'), (u'romansh', u'Romansh'), (u'russian', u'Russian'), (u'sanskrit', u'Sanskrit'), (u'scottish', u'Scottish'), (u'serbian', u'Serbian'), (u'sinhalese', u'Sinhalese'), (u'slovak', u'Slovak'), (u'slovenian', u'Slovenian'), (u'southern ndebele', u'Southern Ndebele'), (u'southern sotho', u'Southern Sotho'), (u'spanish', u'Spanish'), (u'swedish', u'Swedish'), (u'syriac', u'Syriac'), (u'tajik', u'Tajik'), (u'tamil', u'Tamil'), (u'telugu', u'Telugu'), (u'thai', u'Thai'), (u'tibetan', u'Tibetan'), (u'tsonga', u'Tsonga'), (u'tswana', u'Tswana'), (u'turkish', u'Turkish'), (u'turkmen', u'Turkmen'), (u'ukrainian', u'Ukrainian'), (u'urdu', u'Urdu'), (u'uzbek', u'Uzbek'), (u'venda', u'Venda'), (u'vietnamese', u'Vietnamese'), (u'welsh', u'Welsh'), (u'xhosa', u'Xhosa'), (u'zulu', u'Zulu')) # yapf:disable


    name = models.CharField(max_length=100, db_index=True)
    delegation = models.ForeignKey(Delegation, blank=True, null=True)
    hidden = models.BooleanField(default=False)
    hidden_from_submission = models.BooleanField(default=False)
    versioned = models.BooleanField(default=False)
    is_pdf = models.BooleanField(default=False)
    style = models.CharField(max_length=200, blank=True, null=True, choices=STYLES_CHOICES)
    direction = models.CharField(max_length=3, default='ltr', choices=DIRECTION_CHOICES)
    polyglossia = models.CharField(max_length=100, default='english', choices=POLYGLOSSIA_CHOICES)
    polyglossia_options = models.TextField(blank=True, null=True)
    font = models.CharField(
        max_length=100, default='notosans', choices=[(k, v['font']) for k, v in sorted(fonts.ipho.items())]
    )
    extraheader = models.TextField(blank=True)

    class Meta(object):
        unique_together = index_together = (('name', 'delegation'), )

    def natural_key(self):
        return (self.name, ) + self.delegation.natural_key()

    def __str__(self):
        return u'%s (%s)' % (self.name, self.delegation.country)

    def check_permission(self, user):
        if user.is_superuser:
            return True
        else:
            return user.delegation_set.filter(id=self.delegation.pk).exists()

    def is_official(self):
        return self.delegation.name == OFFICIAL_DELEGATION


class ExamManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


@python_2_unicode_compatible
class Exam(models.Model):
    objects = ExamManager()

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True, help_text='Only active exams are editable.')
    hidden = models.BooleanField(default=False, help_text='Is the exam hidden for the delegations?')
    marking_active = models.BooleanField(default=False, help_text='Allow marking submission from delegations.')
    moderation_active = models.BooleanField(default=False, help_text='Allow access to moderation interface.')

    def __str__(self):
        return u'%s' % (self.name)

    def natural_key(self):
        return (self.name, )


class QuestionManager(models.Manager):
    def get_by_natural_key(self, name, exam_name):
        return self.get(name=name, exam=Exam.objects.get_by_natural_key(exam_name))


@python_2_unicode_compatible
class Question(models.Model):
    objects = QuestionManager()

    QUESTION = 0
    ANSWER = 1
    QUESTION_TYPES = (
        (QUESTION, 'Question'),
        (ANSWER, 'Answer'),
    )

    code = models.CharField(
        max_length=8, help_text="e.g. Q for Question, A for Answer Sheet, G for General Instruction"
    )
    name = models.CharField(max_length=100, db_index=True)
    exam = models.ForeignKey(Exam)
    position = models.PositiveSmallIntegerField(help_text='Sorting index inside one exam')
    type = models.PositiveSmallIntegerField(choices=QUESTION_TYPES, default=QUESTION)
    feedback_active = models.BooleanField(default=False, help_text='Are feedbacks allowed?')
    working_pages = models.PositiveSmallIntegerField(default=0, help_text="How many pages for working sheets")

    ## TODO: add template field

    class Meta(object):
        ordering = ['position', 'type']

    def is_answer_sheet(self):
        return self.type == self.ANSWER

    def exam_name(self):
        return self.exam.name

    def __str__(self):
        return u'{} [#{} in {}]'.format(self.name, self.position, self.exam.name)

    def natural_key(self):
        return (self.name, ) + self.exam.natural_key()

    natural_key.dependencies = ['ipho_exam.exam']

    def has_published_version(self):
        return bool(self.versionnode_set.filter(status='C'))

    def check_permission(self, user):
        if user.has_perm('ipho_core.is_staff'):
            return True
        else:
            return self.exam.active


class VersionNodeManager(models.Manager):
    def get_by_natural_key(self, version, question_name, exam_name, lang_name, delegation_name):
        return self.get(
            version=version,
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name)
        )


@python_2_unicode_compatible
class VersionNode(models.Model):
    objects = VersionNodeManager()
    STATUS_CHOICES = (
        ('P', 'Proposal'),
        ('S', 'Staged'),
        ('C', 'Confirmed'),
    )

    text = models.TextField()
    question = models.ForeignKey(Question)
    version = models.IntegerField()
    tag = models.CharField(max_length=100, null=True, blank=True, help_text='leave empty to show no tag')
    language = models.ForeignKey(Language)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = index_together = (('question', 'language', 'version'), )
        ordering = ['-version', '-timestamp']

    def question_name(self):
        return self.question.name

    def __str__(self):
        return u'vnode: {} [{}, v{} {}, {}] - {}'.format(
            self.question.name, self.language, self.version, self.tag, self.timestamp, self.status
        )

    def natural_key(self):
        return (self.version, ) + self.question.natural_key() + self.language.natural_key()

    natural_key.dependencies = ['ipho_exam.question', 'ipho_exam.language']


class TranslationNodeManager(models.Manager):
    def get_by_natural_key(self, question_name, exam_name, lang_name, delegation_name):
        return self.get(
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name)
        )


@python_2_unicode_compatible
class TranslationNode(models.Model):
    objects = TranslationNodeManager()
    STATUS_CHOICES = (
        ('O', 'In progress'),
        ('L', 'Locked'),
        ('S', 'Submitted'),
    )

    text = models.TextField(blank=True)
    question = models.ForeignKey(Question)
    language = models.ForeignKey(Language)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = index_together = (('question', 'language'), )

    def question_name(self):
        return self.question.name

    def __str__(self):
        return u'node: {} [{}, {}] - {}'.format(self.question.name, self.language, self.timestamp, self.status)

    def natural_key(self):
        return self.question.natural_key() + self.language.natural_key()

    natural_key.dependencies = ['ipho_exam.question', 'ipho_exam.language']


class AttributeChangeManager(models.Manager):
    def get_by_natural_key(self, *args, **kwargs):
        return self.get(node=TranslationNode.objects.get_by_natural_key(*args, **kwargs))


@python_2_unicode_compatible
class AttributeChange(models.Model):
    objects = AttributeChangeManager()
    content = models.TextField(blank=True)
    node = models.OneToOneField(TranslationNode)

    def __str__(self):
        return u'attrs:{}'.format(self.node)

    def natural_key(self):
        return self.node.natural_key()

    natural_key.dependencies = [
        'ipho_exam.translationnode',
    ]


class PDFNodeManager(models.Manager):
    def get_by_natural_key(self, question_name, exam_name, lang_name, delegation_name):
        return self.get(
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name)
        )


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('pdfnodes/Lang{}Q{}'.format(instance.question.pk, instance.language.pk), filename)


@python_2_unicode_compatible
class PDFNode(models.Model):
    objects = PDFNodeManager()
    STATUS_CHOICES = (
        ('O', 'In progress'),
        ('L', 'Locked'),
        ('S', 'Submitted'),
    )

    pdf = models.FileField(upload_to=get_file_path, blank=True)
    question = models.ForeignKey(Question)
    language = models.ForeignKey(Language)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = index_together = (('question', 'language'), )

    def question_name(self):
        return self.question.name

    def __str__(self):
        return u'pdfNode: {} [{}, {}] - {}'.format(self.question.name, self.language, self.timestamp, self.status)

    def natural_key(self):
        return self.question.natural_key() + self.language.natural_key()

    natural_key.dependencies = ['ipho_exam.question', 'ipho_exam.language']


@python_2_unicode_compatible
class TranslationImportTmp(models.Model):
    slug = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question)
    language = models.ForeignKey(Language)
    content = models.TextField(blank=True)

    def __str__(self):
        return u'%s - %s, %s' % (self.slug, self.question, self.language)


class FigureManager(PolymorphicManager):
    def get_by_natural_key(self, fig_id):
        return self.get(fig_id=fig_id)


@python_2_unicode_compatible
class Figure(PolymorphicModel):
    objects = FigureManager()
    name = models.CharField(max_length=100, db_index=True)
    fig_id = models.URLField(max_length=100, db_index=True, default=natural_id.generate_id, unique=True, blank=False)

    def natural_key(self):
        return (self.fig_id, )

    def __str__(self):
        return u'%s' % (self.name)


class CompiledFigure(Figure):
    content = models.TextField(blank=True)
    params = models.TextField(blank=True)

    def params_as_list(self):
        return list([si.trim() for si in self.params.split(',')])

    def _to_svg(self, query, lang=None):
        placeholders = self.params.split(',')
        fig_svg = self.content
        fonts_repl = u'@import url({host}/static/noto/notosans.css);'.format(host=SITE_URL)
        font_name = u'Noto Sans'
        text_direction = u'ltr'
        if lang is not None:
            font_name = fonts.ipho[lang.font]['font']
            text_direction = lang.direction
            fonts_repl += '\n@import url({host}/static/noto/{font_css});'.format(
                host=SITE_URL, font_css=fonts.ipho[lang.font]['css']
            )
        fig_svg = fig_svg.replace('%font-faces%', fonts_repl)
        fig_svg = fig_svg.replace('%font-family%', font_name)
        # fig_svg = fig_svg.replace('%text-direction%', text_direction)
        fig_svg = fig_svg.replace('%text-direction%', '')
        for pl in placeholders:
            if pl in query:
                repl = query[pl]
                fig_svg = fig_svg.replace(u'%{}%'.format(pl), repl)
        return fig_svg

    def to_inline(self, query, lang=None):
        return self._to_svg(query=query, lang=lang), 'svg+xml'

    def to_file(self, fig_name, query, lang=None):
        fig_svg = self._to_svg(query=query, lang=lang)
        return self._to_pdf(fig_svg, fig_name)

    @staticmethod
    def _to_pdf(fig_svg, fig_name):
        with open('%s.svg' % (fig_name), 'w') as fp:
            fp.write(fig_svg)
        error = subprocess.Popen(
            [INKSCAPE_BIN, '--without-gui',
             '%s.svg' %
             (fig_name), '--export-pdf=%s.pdf' % (fig_name)],
            stdin=open(os.devnull, "r"),
            stderr=open(os.devnull, "wb"),
            stdout=open(os.devnull, "wb")
        ).wait()
        if error:
            print('Got error', error)
            raise RuntimeError('Error in Inkscape. Errorcode {}.'.format(error))

    # @staticmethod
    # def _to_png(fig_svg, fig_name):
    #     with open('%s.svg' % (fig_name), 'w') as fp:
    #         fp.write(fig_svg)
    #     error = subprocess.Popen(
    #         [INKSCAPE_BIN,
    #          '--without-gui',
    #          '%s.svg' % (fig_name),
    #          '--export-png=%s' % (fig_name),
    #          '--export-dpi=180'],
    #         stdin=open(os.devnull, "r"),
    #         stderr=open(os.devnull, "wb"),
    #         stdout=open(os.devnull, "wb")
    #     ).wait()
    #     if error:
    #         print('Got error', error)
    #         raise RuntimeError('Error in Inkscape. Errorcode {}.'.format(error))


class RawFigure(Figure):
    content = models.BinaryField()
    filetype = models.CharField(max_length=4)
    params = ''

    def params_as_list(self):
        return []

    def to_inline(self, *args, **kwargs):
        return self.content, self.filetype

    def to_file(self, fig_name, query, lang=None, format_default='auto', force_default=False):
        with open('{name}.{ext}'.format(name=fig_name, ext=self.filetype), 'wb') as f:
            f.write(self.content)


class PlaceManager(models.Manager):
    def get_by_natural_key(self, name, exam_name):
        return self.get(name=name, exam__name=exam_name)


@python_2_unicode_compatible
class Place(models.Model):
    objects = PlaceManager()

    student = models.ForeignKey(Student)
    exam = models.ForeignKey(Exam)
    name = models.CharField(max_length=20)

    def __str__(self):
        return u'{} [{} {}]'.format(self.name, self.exam.name, self.student.code)

    def natural_key(self):
        return self.name, self.exam.name

    class Meta(object):
        unique_together = index_together = ('student', 'exam')


@python_2_unicode_compatible
class Feedback(models.Model):
    STATUS_CHOICES = (
        ('S', 'Submitted'),
        ('V', 'Scheduled for voting'),
        ('I', 'Implemented'),
        ('T', 'Settle'),
    )
    PARTS_CHOICES = (
        ('General', 'General'),
        ('Intro', 'Introduction'),
        ('A', 'Part A'),
        ('B', 'Part B'),
        ('C', 'Part C'),
        ('D', 'Part D'),
        ('E', 'Part E'),
        ('F', 'Part F'),
        ('G', 'Part G'),
    )
    SUBPARTS_CHOICES = (
        ('General', 'General comment on part'),
        ('Intro', 'Introduction of part'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    )

    delegation = models.ForeignKey(Delegation)
    question = models.ForeignKey(Question)
    part = models.CharField(max_length=100, default=None)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='S')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'#{} {} - {} ({})'.format(self.pk, self.question.name, self.question.exam.name, self.delegation.name)

    @staticmethod
    def part_id(txt):
        all_parts = []
        for k, v in Feedback.PARTS_CHOICES:
            for kk, vv in Feedback.SUBPARTS_CHOICES:
                all_parts.append('{}.{}'.format(k, kk))
        try:
            i = all_parts.index(txt)
        except:
            print('Problem')
            i = len(all_parts)
        return i


class Like(models.Model):
    CHOICES = (
        ('L', 'Liked'),
        ('U', 'Unliked'),
    )
    status = models.CharField(max_length=1, choices=CHOICES)
    delegation = models.ForeignKey(Delegation)
    feedback = models.ForeignKey(Feedback)

    class Meta(object):
        unique_together = index_together = ('delegation', 'feedback')


class ExamActionManager(models.Manager):
    def get_by_natural_key(self, exam_name, delegation_name, action):
        return self.get(exam__name=exam_name, delegation__name=delegation_name, action=action)


class ExamAction(models.Model):
    objects = ExamActionManager()

    OPEN = 'O'
    SUBMITTED = 'S'
    STATUS_CHOICES = (
        (OPEN, 'In progress'),
        (SUBMITTED, 'Submitted'),
    )
    TRANSLATION = 'T'
    POINTS = 'P'
    ACTION_CHOICES = (
        (TRANSLATION, 'Translation submission'),
        (POINTS, 'Points submission'),
    )
    exam = models.ForeignKey(Exam, related_name='delegation_status')
    delegation = models.ForeignKey(Delegation, related_name='exam_status')
    action = models.CharField(max_length=2, choices=ACTION_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='O')
    timestamp = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = index_together = (('exam', 'delegation', 'action'), )

    def natural_key(self):
        return self.exam.natural_key() + self.delegation.natural_key() + (self.action, )

    natural_key.dependencies = ['ipho_exam.exam', 'ipho_core.delegation']

    @staticmethod
    def is_in_progress(action, exam, delegation):
        translation_submitted = ExamAction.objects.filter(
            exam=exam, delegation=delegation, action=action, status=ExamAction.SUBMITTED
        ).exists()
        return not translation_submitted

    @staticmethod
    def require_in_progress(action, exam, delegation):
        if not ExamAction.is_in_progress(action, exam, delegation):
            raise IphoExamForbidden(
                'You cannot perfom this action more than once. Contact the staff if have good reasons to request a reset.'
            )


@receiver(post_save, sender=Exam, dispatch_uid='create_actions_on_exam_creation')
def create_actions_on_exam_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for delegation in Delegation.objects.all():
        for action, _ in ExamAction.ACTION_CHOICES:
            exam_action, _ = ExamAction.objects.get_or_create(exam=instance, delegation=delegation, action=action)


@receiver(post_save, sender=Delegation, dispatch_uid='create_actions_on_delegation_creation')
def create_actions_on_delegation_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for exam in Exam.objects.all():
        for action, _ in ExamAction.ACTION_CHOICES:
            exam_action, _ = ExamAction.objects.get_or_create(exam=exam, delegation=instance, action=action)


class StudentSubmission(models.Model):
    student = models.ForeignKey(Student)
    exam = models.ForeignKey(Exam)
    language = models.ForeignKey(Language)
    with_answer = models.BooleanField(default=False, help_text='Deliver also answer sheet.')

    ## TODO: do we need a status? (in progress, submitted, printed)

    class Meta(object):
        unique_together = index_together = (('student', 'exam', 'language'), )


def exam_prints_filename(obj, fname):
    basestr = 'exams-docs/{}/print/exam-{}-{}.pdf'
    return basestr.format(obj.student.code, obj.exam.id, obj.position)


def exam_scans_filename(obj, fname):
    basestr = 'exams-docs/{}/scan/exam-{}-{}.pdf'
    return basestr.format(obj.student.code, obj.exam.id, obj.position)


def exam_scans_orig_filename(obj, fname):
    basestr = 'scans-evaluated/{}__{}.pdf'
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    return basestr.format(obj.barcode_base, timestamp)


@python_2_unicode_compatible
class Document(models.Model):
    SCAN_STATUS_CHOICES = (
        ('S', 'Success'),
        ('W', 'Warning'),
        ('M', 'Missing pages'),
    )

    exam = models.ForeignKey(Exam, help_text='Exam')
    student = models.ForeignKey(Student, help_text='Student')
    position = models.IntegerField(
        help_text='Question grouping position, e.g. 0 for cover sheet / instructions, 1 for the first question, etc'
    )
    file = models.FileField(blank=True, upload_to=exam_prints_filename, help_text='Exam handouts')
    num_pages = models.IntegerField(default=0, help_text='Number of pages of the handouts')
    barcode_num_pages = models.IntegerField(default=0, help_text='Number of pages with a barcode')
    extra_num_pages = models.IntegerField(
        default=0, help_text='Number of additional pages with barcode (not in the handouts)'
    )
    barcode_base = models.TextField(help_text='Common base barcode on all pages')
    scan_file = models.FileField(
        blank=True,
        upload_to=exam_scans_filename,
        help_text=
        'Scanned results. The file is show to the delegation and, if possible, it will contain only the pages with barcode.'
    )
    scan_file_orig = models.FileField(
        blank=True, upload_to=exam_scans_orig_filename, help_text='Original scanned document without page extractions'
    )
    scan_status = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=SCAN_STATUS_CHOICES,
        help_text='Status of the scanned document. S - Success, W - Warning, M - Missing pages'
    )
    scan_msg = models.TextField(blank=True, null=True, help_text='Warning messages generated by the barcode extractor')

    class Meta(object):
        unique_together = index_together = (('exam', 'student', 'position'), )

    def question_name(self):
        return self.question.name

    def __str__(self):
        return u'Document: {} #{} [{}]'.format(self.exam.name, self.position, self.student.code)


@python_2_unicode_compatible
class DocumentTask(models.Model):
    task_id = models.CharField(unique=True, max_length=255)
    document = models.OneToOneField(Document)

    def __str__(self):
        return u'{} --> {}'.format(self.task_id, self.document)


@python_2_unicode_compatible
class PrintLog(models.Model):
    TYPE_CHOICES = (('P', 'Printout'), ('S', 'Scan'))
    document = models.ForeignKey(Document)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'{}-{} ({}) {}'.format(self.document.exam.code, self.document.position, self.type, self.timestamp)
