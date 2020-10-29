# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

import os.path
import json
from django.conf import settings
from django import forms
from django.forms import ModelForm, Form, MultiValueField, MultiWidget  # , HiddenInput, DateInput, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, MultiField, Div, HTML
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError

from ipho_control.models import (
    ExamState,
    get_available_exam_fields,
)


class ExamStateForm(ModelForm):
    settings_prefix = "settings_"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['settings'].required = False

        default_settings = None
        if kwargs.get("instance"):
            default_settings = self.instance.settings
        
        exam_fields = []
        for model_field in get_available_exam_fields():
            exam_fields.append(self.settings_prefix + model_field.name)
            tmp_field = model_field.formfield()
            if default_settings:
                tmp_field.initial = default_settings[model_field.name]
            self.fields[self.settings_prefix + model_field.name] = tmp_field
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter question text'), Field('question'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = True
        self.helper.disable_csrf = False
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.add_input(Submit("submit", "Submit"))

        self.helper.layout = Layout(
            Div(
                Fieldset(
            'ExamState',
            'name',
            "available_to_organizers",
            'description',
            'exam',css_class='col-md-5'),
            Fieldset(
                'Exam Settings',
                *exam_fields,
                css_class='col-md-5'
            ), 
            css_class='row')
        )
        

    def clean(self):
        cleaned_data = super().clean()
        setting_fields = [key for key in cleaned_data if key.startswith(self.settings_prefix)]
        settings = {key[len(self.settings_prefix):]: cleaned_data[key] for key in setting_fields}
        cleaned_data["settings"] = settings
        self.validate_unique()
        for key in setting_fields:
            del cleaned_data[key]
        return cleaned_data

    class Meta:
        model = ExamState
        fields = ["name", "description", "exam", "available_to_organizers", "settings"]
        widgets = {
            "settings": forms.HiddenInput(),
        }