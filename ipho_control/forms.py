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
from django.forms import (
    ModelForm,
    Form,
    MultiValueField,
    MultiWidget,
)  # , HiddenInput, DateInput, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, MultiField, Div, HTML
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError

from ipho_control.models import (
    ExamState,
    get_available_exam_fields,
)

EXAM_STATE_DISABLED_FIELDS = getattr(settings, "CONTROL_EXAM_STATE_DISABLED_FIELDS")


class ExamStateForm(ModelForm):
    exam_settings_prefix = "exam_settings_"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set hidden field to non required
        self.fields["exam_settings"].required = False

        # prepare initial data
        initial_exam_settings = None

        if kwargs.get("instance"):
            initial_exam_settings = self.instance.exam_settings

        exam_fields = []
        for model_field in get_available_exam_fields():
            exam_fields.append(self.exam_settings_prefix + model_field.name)
            tmp_field = model_field.formfield()
            if initial_exam_settings:
                tmp_field.initial = initial_exam_settings[model_field.name]
            self.fields[self.exam_settings_prefix + model_field.name] = tmp_field

        check_choices = self.instance.get_available_checks()
        question_setting_choices = self.instance.get_selectable_question_choices()
        self.fields["checks_warning"] = forms.MultipleChoiceField(
            label="Checks warning the user",
            choices=check_choices,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["checks_error"] = forms.MultipleChoiceField(
            label="Checks throwing an error",
            choices=check_choices,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["available_question_settings"] = forms.MultipleChoiceField(
            label="Question settings available to the organizer",
            choices=question_setting_choices,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )

        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter question text'), Field('question'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = True
        self.helper.disable_csrf = False
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.add_input(Submit("submit", "Submit"))

        self.helper.layout = Layout(
            Div(
                Fieldset(
                    "ExamState",
                    "name",
                    "exam",
                    "position",
                    "available_to_organizers",
                    "before_switching",
                    "description",
                    "checks_warning",
                    "checks_error",
                    "available_question_settings",
                    css_class="col-md-5",
                ),
                Fieldset("Exam Settings", *exam_fields, css_class="col-md-5"),
                css_class="row",
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        setting_fields = [
            key for key in cleaned_data if key.startswith(self.exam_settings_prefix)
        ]
        exam_settings = {
            key[len(self.exam_settings_prefix) :]: cleaned_data[key]
            for key in setting_fields
        }
        cleaned_data["exam_settings"] = exam_settings
        self.validate_unique()
        for key in setting_fields:
            del cleaned_data[key]
        return cleaned_data

    class Meta:
        model = ExamState
        fields = [
            "name",
            "description",
            "exam",
            "position",
            "available_to_organizers",
            "before_switching",
            "exam_settings",
            "checks_warning",
            "checks_error",
            "available_question_settings",
        ]
        widgets = {
            "exam_settings": forms.HiddenInput(),
        }

class SwitchStateForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,exam=None, **kwargs)
        
        #self.fields["state"] = forms.RadioSelect
        
