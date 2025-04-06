from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms


class NewFileForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("file"),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.disable_csrf = True


class NewDirectoryForm(forms.Form):
    directory = forms.SlugField(max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("directory"),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
