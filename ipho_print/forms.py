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

from django import forms
from django.forms import ModelForm, Form
from django.forms.formsets import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, ButtonHolder, Submit
from crispy_forms.layout import Layout, Field, MultiField, Div
from crispy_forms.bootstrap import Accordion, AccordionGroup, FormActions

from django.core.exceptions import ValidationError

from . import printer

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
    duplex = forms.ChoiceField(required=False, initial='None', choices=[('None', 'No'), ('DuplexNoTumble', 'Yes')])
    color = forms.ChoiceField(required=False, initial='Colour', choices=[('Colour', 'Yes'), ('Grayscale', 'No')])
    staple = forms.ChoiceField(required=False, initial='None', choices=[('None', 'No'), ('1PLU', 'Yes')])

    def __init__(self, *args, **kwargs):
        queue_list = kwargs.pop('queue_list')
        enable_opts = kwargs.pop('enable_opts') if 'enable_opts' in kwargs else False
        super(PrintForm, self).__init__(*args, **kwargs)

        self.fields['queue'].choices = queue_list
        default_opts = printer.default_opts()
        opts_map = {'duplex':'Duplex', 'color':'ColourModel', 'staple':'Staple'}
        for k in opts_map:
            self.fields[k].initial = default_opts[opts_map[k]]
        for k in opts_map:
            print(k)
            print(self.fields[k].initial)

        self.helper = FormHelper()
        if enable_opts:
            self.helper.layout = Layout(
                Field('file'), Field('queue'), Field('duplex'), Field('color'), Field('staple'),
                FormActions(Submit('submit', 'Submit'))
            )
        else:
            self.helper.layout = Layout(Field('file'), Field('queue'), FormActions(Submit('submit', 'Submit')))

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = True

    def clean(self):
        cleaned_data = super(PrintForm, self).clean()
        queue = cleaned_data.get("queue")
        allowed_opts = printer.allowed_opts(queue)
        opts_map = {'duplex':'Duplex', 'color':'ColourModel', 'staple':'Staple'}
        for k in opts_map:
            if cleaned_data.get(k) not in ['None', 'Grayscale']:
                if cleaned_data.get(k) != allowed_opts[opts_map[k]]:
                    msg = 'The current printer does not support this option.'
                    self.add_error(k, msg)
