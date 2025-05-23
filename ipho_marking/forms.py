from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings
from django.forms import Form, ModelForm

from ipho_exam.models import Exam

from .models import Marking

ALLOW_MARKS_NONE = getattr(settings, "ALLOW_MARKS_NONE", False)


class UploadMarkingForm(Form):
    file = forms.FileField()


class ImportForm(Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.filter(
            visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT
        ).all(),
        label="Select exam",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit"))

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = True


class PointsForm(ModelForm):
    def __init__(self, *args, require_points=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "points"
        ].label = f"{self.instance.marking_meta.name} ({self.instance.marking_meta.min_points},{self.instance.marking_meta.max_points})"
        self.fields["points"].required = not ALLOW_MARKS_NONE or require_points
        self.fields["comment"].required = False

        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False

    class Meta:
        model = Marking
        fields = [
            "points",
        ]
        widgets = {
            "points": forms.TextInput(
                attrs={"style": "width:55px", "class": "form-control"}
            ),
            "comment": forms.Textarea(attrs={"class": "form-control"}),
        }
