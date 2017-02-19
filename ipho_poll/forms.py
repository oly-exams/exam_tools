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

from django import forms
from django.forms import ModelForm, Form, HiddenInput, DateInput, RadioSelect
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div, HTML
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError

from ipho_poll.models import Question, Choice, Vote



class QuestionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter question text'), Field('question'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = Question
        fields = ['title', 'content', 'feedbacks']


class EndDateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EndDateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
                                    Field('end_date', id="modal-datetimepicker"),
                                    HTML('<div class="quick-end-time" data-min="1"></div>'),
                                    HTML('<div class="quick-end-time" data-min="2"></div>'),
                                    HTML('<div class="quick-end-time" data-min="5"></div>'),
                                    HTML('<div class="quick-end-time" data-min="10"></div>'),
                                    )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = True
    class Meta:
        model = Question
        fields = ['end_date']
        localized_fields = ['end_date',]
        widgets={'end_date': HiddenInput()}


class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['label', 'choice_text']
        widgets = {
            'label': forms.TextInput(attrs={'size':3, 'maxlength':3}),
        }

class ChoiceFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ChoiceFormHelper, self).__init__(*args, **kwargs)
        self.layout =   Layout(
                            Div(
                                Div(Field('label'), css_class='form-group'),
                                Div(Field('choice_text', placeholder='Enter choice text'), css_class='form-group'),
                                Div(Field('DELETE')),
                                css_class='form-inline'

                            )
                        )
        self.form_show_labels = True
        self.html5_required = False
        self.form_tag = False
        self.disable_csrf = True


class VoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(VoteForm, self).__init__(*args, **kwargs)
        self.fields['choice'].empty_label = None
        if self.instance.pk is not None:
            self.fields['choice'].label = self.instance.voting_right
        elif not self.is_bound:
            self.fields['choice'].label = self.initial['voting_right']
        ## Note: in the case of a bound form the label will still be "Choice". Unfortunately I didn't find a workaround
    class Meta:
        model = Vote
        fields = ['choice', 'question', 'voting_right']
        widgets={'choice': RadioSelect(), 'voting_right': HiddenInput()}
class VoteFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(VoteFormHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
                        Div(Field('choice')),
                        Div(Field('question'))
        )
        self.form_show_labels = True
        self.html5_required = False
        self.form_tag = False
        self.disable_csrf = False
