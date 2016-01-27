from django import forms
from django.forms import ModelForm, Form
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div
from django.utils.safestring import mark_safe

from django.core.exceptions import ValidationError


from ipho_poll.models import Question, Choice, Vote



class QuestionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Field('question_text', placeholder='Enter question text'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = Question
        fields = ['question_text']


class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']
class ChoiceFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ChoiceFormHelper, self).__init__(*args, **kwargs)
        self.layout =   Layout(
                            Div(
                                Div(Field('choice_text', placeholder='Enter choice text'), css_class='form-group'),
                                css_class='form-inline'
                            )
                        )
        self.form_show_labels = True
        self.html5_required = True
        self.form_tag = False
        self.disable_csrf = True

class VoteForm(ModelForm):
    class Meta:
        model = Vote
        fields = ['choice']
