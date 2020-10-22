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

from django import forms
from django.forms import ModelForm, Form  # , HiddenInput, DateInput, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div, HTML
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError

from ipho_control.models import (
    ExamState,
    ExamStateTransition,
    get_available_exam_fields,
)


class ExamStateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for model_field in get_available_exam_fields():
            self.fields["settings_" + model_field.name] = model_field.formfield()
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter question text'), Field('question'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean(self):
        cleaned_data = super().clean()

        # create settings json and add it to cleaned data
        setting_fields = [key for key in cleaned_data if key.startswith("settings_")]
        settings = {key: cleaned_data[key] for key in setting_fields}
        cleaned_data["settings"] = settings
        for key in setting_fields:
            del cleaned_data[key]
        return cleaned_data

    class Meta:
        model = ExamState
        fields = ["name", "description", "exam", "available_to_organizers"]


class ExamStatTransitionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter question text'), Field('question'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        for model_field in get_available_exam_fields():
            self.fields["settings_" + model_field.name] = model_field.formfield()

    def clean(self):
        cleaned_data = super().clean()

        # create settings json and add it to cleaned data
        setting_fields = [key for key in cleaned_data if key.startswith("settings_")]
        settings = {key: cleaned_data[key] for key in setting_fields}
        cleaned_data["settings"] = settings
        for key in setting_fields:
            del cleaned_data[key]
        return cleaned_data

    class Meta:
        model = ExamStateTransition
        fields = ["name", "description", "from_state", "to_state"]
