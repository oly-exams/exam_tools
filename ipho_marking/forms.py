# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
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
        self.fields['points'].label = '{} ({})'.format(
            self.instance.marking_meta.name, self.instance.marking_meta.max_points
        )
        self.fields['points'].required = True

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        # self.helper.disable_csrf = False
        # self.disable_csrf = False
        self.helper.form_tag = False

    class Meta(object):
        model = Marking
        fields = [
            'points',
        ]
        widgets = {'points': forms.TextInput(attrs={'style': 'width:50px', 'class': 'form-control'})}
