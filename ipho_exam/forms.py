from __future__ import print_function
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

from builtins import object
from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div, Fieldset
from crispy_forms.bootstrap import Accordion, AccordionGroup, FormActions
from django.utils.safestring import mark_safe

import decimal

from django.core.exceptions import ValidationError

from ipho_exam.models import Language, Question, Student, Figure, VersionNode, TranslationNode, PDFNode, Feedback, StudentSubmission, TranslationImportTmp, Document


def build_extension_validator(valid_extensions):
    def validate_file_extension(value):
        import os
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        # valid_extensions = ['.svg', '.svgz']
        if not ext in valid_extensions:
            raise ValidationError(u'Unsupported file extension.')

    return validate_file_extension


class LanguageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_delegation = kwargs.pop('user_delegation')
        super(LanguageForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', placeholder='Name'),
            Field('style'),
            Accordion(
                AccordionGroup(
                    'Advanced settings',
                    Field('direction'),
                    Field('polyglossia'),
                    Field('polyglossia_options'),
                    Field('font'),
                    active=False,
                ),
            ),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'exam:main'
        # self.helper.add_input(Submit('submit', 'Create'))

    def clean_name(self):
        data = self.cleaned_data['name']
        if "_" in data:
            raise forms.ValidationError("Underscore '_' symbols are forbidden in language names.")
        return data

    def clean(self):
        cleaned_data = super(LanguageForm, self).clean()

        try:
            Language.objects.get(name=cleaned_data['name'], delegation=self.user_delegation)
        except Language.DoesNotExist:
            pass
        else:
            if not self.instance or not self.instance.pk:
                raise ValidationError(
                    'This language already exist for delegation ' + self.user_delegation.name +
                    '. Enter a different name.'
                )

        # Always return cleaned_data
        return cleaned_data

    class Meta(object):
        model = Language
        fields = ['name', 'style', 'direction', 'polyglossia', 'polyglossia_options', 'font']
        labels = {
            'name':
            'Name of the language version (e.g. Swiss German)',
            'direction':
            ' Writing Direction',
            'style':
            'Language style <a href="#" data-toggle="popover" data-trigger="hover" data-html="true" data-container="body" data-content="Select a language similar to yours or leave <emph>english</emph>. This will preset the advanced settings."><span class="glyphicon glyphicon-info-sign"></span></a>',
            'polyglossia':
            'Polyglossia style <a href="#" data-toggle="popover" data-trigger="hover" data-html="true" data-container="body" data-content="Select a language similar to yours or leave <emph>english</emph>. This will improve the final typesetting, e.g. allowing correct hyphenation."><span class="glyphicon glyphicon-info-sign"></span></a>',
            'font':
            'Font in PDF <a href="#" data-toggle="popover" data-trigger="hover" data-html="true" data-container="body" data-content="For most languages choose <emph>Noto Sans</emph>. Preview of Noto fonts is available <a href=\'https://www.google.com/get/noto\' target=\'_blank\'>here</a>. More fonts can be added on request."><span class="glyphicon glyphicon-info-sign"></span></a>',
            'polyglossia_options':
            'Polyglossia options <a href="#" data-toggle="popover" data-trigger="hover" data-html="true" data-container="body" data-content="Advanced setting, please refer to the staff before editing"><span class="glyphicon glyphicon-info-sign"></span></a>',
        }
        widgets = {'polyglossia_options': forms.TextInput()}


class FigureForm(ModelForm):
    def __init__(self, *args, **kwargs):
        valid_extensions = kwargs.pop('valid_extensions', ('.svg', '.svgz', '.png', '.jpg', '.jpeg'))
        super(FigureForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['file'] = forms.FileField(
            validators=[build_extension_validator(valid_extensions)],
            label=
            'Figure file <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Allowed filetypes: {}"><span class="glyphicon glyphicon-info-sign"></span></a>'.
            format(' '.join('*' + ext for ext in valid_extensions))
        )
        if instance and instance.pk:
            self.fields['file'].required = False

        self.helper = FormHelper()
        self.helper.layout = Layout(Field('name', placeholder='Enter figure name'), Field('file'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = Figure
        fields = ['name']


class TranslationForm(forms.Form):
    language = forms.ModelChoiceField(queryset=Language.objects.none())

    def __init__(self, *args, **kwargs):
        super(TranslationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('name', placeholder='Name'),
        #                             Field('polyglossia'),
        #                             )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'exam:index'
        # self.helper.add_input(Submit('submit', 'Create'))

    class Meta(object):
        fields = ['language']
        labels = {
            'language':
            'Language <a href="#" onclick="return false;" data-toggle="popover" data-trigger="hover" data-container="body" data-content="More languages can be created from the Exam > Languages interface."><span class="glyphicon glyphicon-info-sign"></span></a>',
        }


class ExamQuestionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExamQuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = Question
        fields = ['code', 'name', 'position', 'type', 'working_pages']
        labels = {
            'code': 'Code',
            'name': 'Name',
            'position': 'Position',
            'type': 'Type',
            'working_pages': 'Working Pages (only valid for Type Answer)',
        }


class DeleteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        print("hello world from delete form")
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    verify = forms.CharField(max_length=100, label='Please type in the name of the question to confirm.')


class VersionNodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(VersionNodeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = VersionNode
        fields = ['tag']
        labels = {
            'tag': 'Tag',
        }


class PDFNodeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PDFNodeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = PDFNode
        fields = [
            'pdf',
        ]
        labels = {'pdf': 'Select new file to upload'}
        widgets = {'pdf': forms.FileInput()}


class TranslationImportForm(ModelForm):
    file = forms.FileField(
        validators=[build_extension_validator(['.xml', '.qml'])],
        label=
        'Question file <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Allowed filetypes: *.xml"><span class="glyphicon glyphicon-info-sign"></span></a>'
    )

    def __init__(self, *args, **kwargs):
        super(TranslationImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = TranslationImportTmp
        fields = []


class FeedbackForm(ModelForm):
    part_nr = forms.ChoiceField(widget=forms.Select(), choices=Feedback.PARTS_CHOICES, label='Which part?')
    subpart_nr = forms.ChoiceField(
        widget=forms.Select(), required=False, choices=Feedback.SUBPARTS_CHOICES, label='Which subpart?'
    )

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['question'].label_from_instance = lambda obj: obj.name

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('question'),
            Div(
                Div(
                    Fieldset('', 'part_nr', css_class='col-md-6'),
                    Fieldset('', 'subpart_nr', css_class='col-md-6'),
                    css_class='row'
                ),
                css_class='container-fluid'
            ),
            Field('comment', placeholder='Comment'),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True

    class Meta(object):
        model = Feedback
        fields = ['question', 'comment']
        # labels = {'part': 'Question part'}


class SubmissionAssignForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SubmissionAssignForm, self).__init__(*args, **kwargs)
        self.fields['student'].label_from_instance = lambda obj: u'{} {}'.format(obj.first_name, obj.last_name)

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        # self.helper.disable_csrf = False
        # self.disable_csrf = False
        self.helper.form_tag = False
        #self.form_tag = False

    class Meta(object):
        model = StudentSubmission
        fields = ['student', 'language', 'with_answer']


class AssignTranslationForm(forms.Form):
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.none(), widget=forms.widgets.CheckboxSelectMultiple
    )
    main_language = forms.ModelChoiceField(queryset=Language.objects.none(), widget=forms.widgets.RadioSelect)

    def __init__(self, *args, **kwargs):
        languages_queryset = kwargs.pop('languages_queryset')
        super(AssignTranslationForm, self).__init__(*args, **kwargs)
        self.fields['languages'].queryset = languages_queryset
        self.fields['main_language'].queryset = languages_queryset

    def clean(self):
        cleaned_data = super(AssignTranslationForm, self).clean()
        languages = cleaned_data.get("languages")
        main_language = cleaned_data.get("main_language")
        if languages and main_language and main_language not in languages:
            msg = "Answer language not enabled."
            self.add_error('languages', msg)


## ungly hack to propagate `languages_queryset` attribute to form construction
BaseAssignTranslationFormSet = formset_factory(AssignTranslationForm)


class AssignTranslationFormSet(BaseAssignTranslationFormSet):
    def __init__(self, languages_queryset, *args, **kwargs):
        self.languages_queryset = languages_queryset
        super(AssignTranslationFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, *args, **kwargs):
        kwargs['languages_queryset'] = self.languages_queryset
        return super(AssignTranslationFormSet, self)._construct_form(*args, **kwargs)


class AdminImportForm(forms.Form):
    file = forms.FileField(
        validators=[build_extension_validator(['.xml', '.qml'])],
        label=
        'Question file <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Allowed filetypes: *.xml"><span class="glyphicon glyphicon-info-sign"></span></a>'
    )

    def __init__(self, *args, **kwargs):
        super(AdminImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.helper.disable_csrf = True


class AdminBlockAttributeForm(forms.Form):
    key = forms.CharField()
    value = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(AdminBlockAttributeForm, self).__init__(*args, **kwargs)
        self.disable_csrf = True

    def clean(self):
        cleaned_data = super(AdminBlockAttributeForm, self).clean()
        if cleaned_data['key'] == 'points':
            try:
                cont = decimal.Context(prec=28, rounding=decimal.ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                        capitals=1, clamp=0, flags=[], traps=[decimal.Overflow,
                        decimal.InvalidOperation, decimal.Inexact])
                decimal.setcontext(cont)
                decimal.getcontext().clear_flags()
                points = decimal.Decimal(cleaned_data['value']).quantize(decimal.Decimal('0.01')) #constraints given from marking model Decimal field
                if points>= decimal.Decimal('1000000'):
                    raise ValueError('points too large')
            except (decimal.Inexact, decimal.Overflow, decimal.InvalidOperation, ValueError) as e:
                msg = "'points' can only have 2 decimal places and need to be smaller than 1000000 . (e.g. 1.25)"
                self.add_error('value', msg)
        return cleaned_data

class AdminBlockAttributeHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AdminBlockAttributeHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
            Div(
                Div(Field('key', placeholder='key'), css_class='form-group'),
                Div(Field('value', placeholder='value'), css_class='form-group'),
                css_class='form-inline'
            )
        )
        #self.html5_required = True
        self.form_show_labels = True
        self.form_tag = False
        self.disable_csrf = True


AdminBlockAttributeFormSet = formset_factory(AdminBlockAttributeForm, can_delete=True, extra=2)


class AdminBlockForm(forms.Form):
    def __init__(self, node, *args, **kwargs):
        super(AdminBlockForm, self).__init__(*args, **kwargs)
        if node.has_text:
            self.fields['block_content'] = node.form_element()
            self.fields['block_content'].initial = mark_safe(node.content())
            self.fields['block_content'].required = False
            self.fields['block_content'].widget.attrs['class'] = 'block-content-editor'
        # for k,v in node.attributes.items():
        #     self.fields['attribute_'+k] = forms.CharField()
        #     self.fields['attribute_'+k].initial = v

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.disable_csrf = True
        self.form_tag = False
        self.disable_csrf = True


class PrintDocsForm(forms.Form):
    queue = forms.ChoiceField(choices=[], label='Print queue to use')
    duplex = forms.ChoiceField(initial='None', choices=[('None', 'No'), ('DuplexNoTumble', 'Yes')])
    color = forms.ChoiceField(initial='Colour', choices=[('Colour', 'Yes'), ('Grayscale', 'No')])
    staple = forms.ChoiceField(initial='None', choices=[('None', 'No'), ('1PLU', 'Yes')])

    def __init__(self, *args, **kwargs):
        queue_list = kwargs.pop('queue_list')
        super(PrintDocsForm, self).__init__(*args, **kwargs)

        self.fields['queue'].choices = queue_list

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('queue'), Field('duplex'), Field('color'), Field('staple'), FormActions(Submit('submit', 'Print'))
        )

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False


class ScanForm(forms.Form):
    question = forms.ModelChoiceField(queryset=Question.objects.all())
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    file = forms.FileField(validators=[build_extension_validator(['.pdf'])])

    def __init__(self, *args, **kwargs):
        super(ScanForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('question'), Field('student'), Field('file'), FormActions(Submit('submit', 'Upload'))
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True


class ExtraSheetForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    quantity = forms.IntegerField()
    template = forms.ChoiceField(
        widget=forms.RadioSelect, choices=(
            ('exam_blank.tex', 'Blank sheets'),
            ('exam_graph.tex', 'Graph sheets'),
        )
    )

    def __init__(self, exam_id, *args, **kwargs):
        super(ExtraSheetForm, self).__init__(*args, **kwargs)
        self.fields['question'] = forms.ModelChoiceField(queryset=Question.objects.filter(exam_id=exam_id, code='Q'))
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('question'), Field('student'), Field('quantity'), Field('template'),
            FormActions(Submit('submit', 'Generate'))
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
