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

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout, Submit
from django import forms
from django.forms import ModelForm

from ipho_core.models import AccountRequest, User


class AccountRequestForm(ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.exclude(delegation__isnull=True)
        .exclude(is_superuser=True)
        .order_by("username"),
        to_field_name="username",
        label="Delegation",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("email"), Field("user"), FormActions(Submit("submit", "Submit"))
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True

    class Meta:
        model = AccountRequest
        fields = ["email", "user"]


class SendPushForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("to_all"),
            Field("message"),
            Field("url"),
            FormActions(Submit("submit", "Submit")),
            Field("users"),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(is_superuser=True).order_by("username").all(),
        label="select users",
        required=False,
        widget=forms.widgets.CheckboxSelectMultiple,
    )
    to_all = forms.BooleanField(
        required=False, label="send to all users (choose individual users below)"
    )
    message = forms.CharField(label="Message to send")
    url = forms.URLField(label="url to redirect users to", required=False)


class RandomDrawForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("do_it"),
            FormActions(Submit("submit", "Submit")),
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True

    do_it = forms.BooleanField()
