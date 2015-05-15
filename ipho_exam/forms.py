from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

from django.core.exceptions import ValidationError


from ipho_exam.models import Language, Figure

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.svg', '.svgz']
    if not ext in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


class LanguageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LanguageForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['name'].widget.attrs['readonly'] = True
        
        
        self.helper = FormHelper()
        self.helper.layout = Layout(Field('name', placeholder='Name'),
                                    Field('polyglossia'),
                                    )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.disable_csrf = True
        # self.helper.form_method = 'post'
        # self.helper.form_action = 'exam:index'
        # self.helper.add_input(Submit('submit', 'Create'))
        
    class Meta:
        model = Language
        fields = ['name','polyglossia']
        labels = {
                   'polyglossia': 'Language style <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Select a lanugage similar to yours. This will improve the final typesetting, e.g. allowing correct hyphenation."><span class="glyphicon glyphicon-info-sign"></span></a>',
               }

class FigureForm(ModelForm):
    file = forms.FileField(validators=[validate_file_extension], label='Figure file <a href="#" data-toggle="popover" data-trigger="hover" data-container="body" data-content="Allowed filetypes: *.svg, *.svgz"><span class="glyphicon glyphicon-info-sign"></span></a>')
    
    def __init__(self, *args, **kwargs):
        super(FigureForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['file'].required = False
        
        self.helper = FormHelper()
        self.helper.layout = Layout(Field('name', placeholder='Enter figure name'),
                                    Field('file')
                                    )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = False
        self.disable_csrf = True
    
    
    class Meta:
        model = Figure
        fields = ['name']
