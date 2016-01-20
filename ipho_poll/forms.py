from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError


from ipho_poll.models import Question



class QuestionForm(ModelForm):
        def __init__(self, *args, **kwargs):
            super(QuestionForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(Field('question_text', placeholder='Enter question text'))
            self.helper.html5_required = True
            self.helper.form_show_labels = True


        class Meta:
            model = Question
            fields = ['question_text']
