from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from ipho_exam.models import Language


class LanguageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Field('name', placeholder='Name'),
                                    Field('polyglossia'),
                                    )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'exam:index'
        # self.helper.add_input(Submit('submit', 'Create'))
        
    class Meta:
        model = Language
        fields = ['name','polyglossia']
        labels = {
                   'polyglossia': 'Language style <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Select a lanugage similar to yours. This will improve the final typesetting, e.g. allowing correct hyphenation."><span class="glyphicon glyphicon-info-sign"></span></a>',
               }
