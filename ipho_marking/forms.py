from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from django.forms.models import BaseInlineFormSet, inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div
from crispy_forms.bootstrap import Accordion, AccordionGroup

from ipho_exam.models import Exam
from .models import MarkingMeta, Marking

class ImportForm(Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.all(), label='Select exam')

    def __init__(self, *args, **kwargs):
        super(ImportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = True

class PointsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PointsForm, self).__init__(*args, **kwargs)
        self.fields['points'].label = self.instance.marking_meta.name
        self.fields['points'].widget.attrs={'style': 'width:50px'}

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        # self.helper.disable_csrf = False
        # self.disable_csrf = False
        self.helper.form_tag = False
    class Meta:
        model = Marking
        fields = ['points',]
