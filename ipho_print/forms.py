from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, ButtonHolder, Submit
from crispy_forms.layout import Layout, Field, MultiField, Div
from crispy_forms.bootstrap import Accordion, AccordionGroup, FormActions

from django.core.exceptions import ValidationError

def build_extension_validator(valid_extensions):
    def validate_file_extension(value):
        import os
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        # valid_extensions = ['.svg', '.svgz']
        if not ext in valid_extensions:
            raise ValidationError(u'Unsupported file extension.')
    return validate_file_extension


class PrintForm(forms.Form):
    file = forms.FileField(validators=[build_extension_validator(['.pdf'])], label='PDF document to print')
    queue = forms.ChoiceField(choices=[], label='Print queue to use')

    def __init__(self, *args, **kwargs):
        queue_list = kwargs.pop('queue_list')
        super(PrintForm, self).__init__(*args, **kwargs)

        self.fields['queue'].choices = queue_list

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('file'),
            Field('queue'),
            FormActions(
                Submit('submit', 'Submit')
            )
        )

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = True
