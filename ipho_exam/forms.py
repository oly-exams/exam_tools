from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from ipho_exam.models import Language


class LanguageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Field('name', placeholder='Name'),)
        self.helper.html5_required = True
        self.helper.form_show_labels = False
        self.helper.form_method = 'post'
        self.helper.form_action = 'exam:index'
        self.helper.add_input(Submit('submit', 'Create'))
        
    class Meta:
        model = Language
        fields = ['name']
