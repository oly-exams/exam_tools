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
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, MultiField, Div, Fieldset
from crispy_forms.bootstrap import Accordion, AccordionGroup, FormActions

from django.core.exceptions import ValidationError

from ipho_core.models import User, AccountRequest


class AccountRequestForm(ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.exclude(delegation__isnull=True).exclude(autologin__isnull=True).exclude(is_superuser=True).order_by('username'),
        to_field_name='username',
        label='Delegation'
    )

    def __init__(self, *args, **kwargs):
        super(AccountRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('email'),
            Field('user'),
            FormActions(
                Submit('submit', 'Submit')
            )
        )
        self.helper.html5_required = True
        self.helper.form_show_labels = True

    class Meta:
        model = AccountRequest
        fields = ['email', 'user']
