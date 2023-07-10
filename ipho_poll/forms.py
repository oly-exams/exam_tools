# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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
from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput, RadioSelect, BaseInlineFormSet
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML


from ipho_exam.models import Feedback
from ipho_poll.models import Voting, VotingChoice, CastedVote


class VotingForm(ModelForm):
    feedbacks = forms.ModelMultipleChoiceField(Feedback.objects.order_by('pk'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.layout = Layout(Field('title', placeholder='Enter voting text'), Field('voting'))
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    class Meta:
        model = Voting
        fields = ["title", "content", "feedbacks"]


class EndDateForm(ModelForm):
    utc_offset = forms.IntegerField(
        widget=HiddenInput(), help_text="UTC offset in minutes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<span class="quick-end-time" data-min="1"></span>'),
            HTML('<span class="quick-end-time" data-min="2"></span>'),
            HTML('<span class="quick-end-time" data-min="5"></span>'),
            HTML('<span class="quick-end-time" data-min="10"></span>'),
            HTML(
                '<p/><a href="#advanced" data-toggle="collapse">Advanced</a><div id="advanced" class="collapse">'
            ),
            Field("utc_offset", id="modal-utc_offset"),
            Field("end_date", id="modal-datetimepicker"),
            HTML("</div>"),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.include_media = True

    class Meta:
        model = Voting
        fields = ["end_date"]
        widgets = {"end_date": HiddenInput()}


class VotingChoiceForm(ModelForm):
    class Meta:
        model = VotingChoice
        fields = ["label", "choice_text"]
        widgets = {
            "label": forms.TextInput(attrs={"size": 3, "maxlength": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            linit = kwargs["initial"]["label"]
        except KeyError:
            linit = ""
        try:
            linst = kwargs["instance"].label
        except (KeyError, TypeError):
            linst = ""
        if linit == "zzz" or linst == "zzz":
            self.fields["label"].widget.attrs["readonly"] = True
            self.fields["choice_text"].widget.attrs["readonly"] = True


class VotingChoiceFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        can_delete = kwargs.pop("can_delete", True)
        super().__init__(*args, **kwargs)

        fields = [
            Div(Field("label"), css_class="form-group"),
            Div(
                Field("choice_text", placeholder="Enter choice text"),
                css_class="form-group",
            ),
        ]
        if can_delete:
            fields += [Div(Field("DELETE"))]
        self.layout = Layout(Div(*fields, css_class="form-inline"))
        self.form_show_labels = True
        self.html5_required = False
        self.form_tag = False
        self.disable_csrf = True


class CastedVoteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["choice"].empty_label = None
        if self.instance.pk is not None:
            self.fields["choice"].label = self.instance.voting_right
        elif not self.is_bound:
            self.fields["choice"].label = self.initial["voting_right"]
        ## Note: in the case of a bound form the label will still be "Choice". Unfortunately I didn't find a workaround

    class Meta:
        model = CastedVote
        fields = ["choice", "voting", "voting_right"]
        widgets = {"choice": RadioSelect(), "voting_right": HiddenInput()}


class CastedVoteBaseFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        all_none = True
        for form in self.forms:
            if form.cleaned_data.get("choice") is not None:
                all_none = False
        if all_none:
            raise ValidationError("Please submit at least one vote.")
        for errordict in self.errors:
            if errordict.get(
                "__all__"
            ) and "Casted vote with this Voting and Voting right already exists." in errordict.get(
                "__all__"
            ):
                for error in errordict.get("__all__").as_data():
                    if error.code == "unique_together":
                        error.message = "This vote has already been cast (maybe on another device). Please reload the page."


class CastedVoteFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = Layout(Div(Field("choice")), Div(Field("voting")))
        self.form_show_labels = True
        self.html5_required = False
        self.form_tag = False
        self.disable_csrf = False
