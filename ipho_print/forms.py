import os
import random

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError

from . import printer


def build_extension_validator(valid_extensions):
    def validate_file_extension(value):

        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        # valid_extensions = ['.svg', '.svgz']
        if not ext in valid_extensions:
            raise ValidationError("Unsupported file extension.")

    return validate_file_extension


class PrintForm(forms.Form):
    file = forms.FileField(
        validators=[build_extension_validator([".pdf"])], label="PDF document to print"
    )
    queue = forms.ChoiceField(choices=[], label="Print queue to use")
    duplex = forms.ChoiceField(
        required=False,
        initial="None",
        choices=[("None", "No"), ("DuplexNoTumble", "Yes")],
    )
    color = forms.ChoiceField(
        required=False, initial="Colour", choices=[("Colour", "Yes"), ("Gray", "No")]
    )
    staple = forms.ChoiceField(
        required=False, initial="None", choices=[("None", "No"), ("1PLU", "Yes")]
    )

    def __init__(self, *args, **kwargs):
        queue_list = kwargs.pop("queue_list")
        self.enable_opts = (
            kwargs.pop("enable_opts") if "enable_opts" in kwargs else False
        )
        super().__init__(*args, **kwargs)
        if not self.enable_opts:
            random.shuffle(queue_list)

        self.fields["queue"].choices = queue_list
        if self.enable_opts:
            default_opts = printer.default_opts()
        else:
            default_opts = printer.delegation_opts()

        opts_map = {"duplex": "Duplex", "color": "ColourModel", "staple": "Staple"}
        for k, val in opts_map.items():
            self.initial[k] = default_opts[val]

        self.helper = FormHelper()
        if self.enable_opts:
            self.helper.layout = Layout(
                Field("file"),
                Field("queue"),
                Field("duplex"),
                Field("color"),
                Field("staple"),
                FormActions(Submit("submit", "Submit")),
            )
        else:
            self.helper.layout = Layout(
                Field("file"),
                Field("queue"),
                FormActions(Submit("submit", "Submit")),
                Field("duplex", type="hidden"),
                Field("color", type="hidden"),
                Field("staple", type="hidden"),
            )

        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.form_tag = True

    def clean(self):
        cleaned_data = super().clean()
        queue = cleaned_data.get("queue")
        print(cleaned_data)
        allowed_opts = printer.allowed_opts(queue)
        opts_map = {"duplex": "Duplex", "color": "ColourModel", "staple": "Staple"}
        for k, val in opts_map.items():
            if cleaned_data.get(k) not in ["None", "Gray"]:

                if cleaned_data.get(k) != allowed_opts[val]:
                    if self.enable_opts:
                        msg = "The current printer does not support this option."
                        self.add_error(k, msg)
                    else:
                        cleaned_data[k] = allowed_opts[val]
        return cleaned_data
