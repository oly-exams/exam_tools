# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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

import inspect
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from ipho_exam.models import Exam, Question

import ipho_control.state_checks as state_checks

EXAM_STATE_DISABLED_FIELDS = getattr(settings, "CONTROL_EXAM_STATE_DISABLED_FIELDS")
EXAM_STATE_QUESTION_FIELDS = getattr(settings, "CONTROL_EXAM_STATE_QUESTION_FIELDS")


def get_available_exam_fields():
    # TODO: should this be a staticmethod of Exam?
    all_fields = Exam._meta.get_fields()
    available_fields = [
        field
        for field in all_fields
        if field.name not in EXAM_STATE_DISABLED_FIELDS
        and hasattr(field, "default")
        and field.default is not models.fields.NOT_PROVIDED
    ]
    available_fields.sort(key=lambda o: o.name)
    return available_fields


def get_default_exam_state_settings():
    available_fields = get_available_exam_fields()
    default_settings = {f.name: f.default for f in available_fields}
    return default_settings


def get_selectable_question_fields():
    all_fields = Question._meta.get_fields()
    available_fields = [
        field for field in all_fields if field.name in EXAM_STATE_QUESTION_FIELDS
    ]
    available_fields.sort(key=lambda o: o.name)
    return available_fields


class ExamStateManager(models.Manager):
    def get_by_natural_key(self, name, exam):
        return self.get(name=name, exam=Exam.objects.get_by_natural_key(exam))


class ExamState(models.Model):
    objects = ExamStateManager()

    position = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()

    before_switching = models.TextField(null=True, blank=True, help_text="Text displayed when confirming switching to this state.")

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    available_to_organizers = models.BooleanField(
        default=True, help_text="Let's the organizers see and select this state"
    )

    exam_settings = models.JSONField(
        default=get_default_exam_state_settings,
        help_text="A dictionnary containing fields and settings.",
    )

    available_question_settings = models.JSONField(
        default=list,
        help_text="A list of question fields.",
        null=True,
        blank=True,
    )

    checks_warning = models.JSONField(
        default=list,
        help_text="A list of checks which can trigger a warnign when applying the transition.",
        null=True,
        blank=True,
    )

    checks_error = models.JSONField(
        default=list,
        help_text="A list of checks which can prevent the transition.",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exam", "name"], name="Unique name"),
            models.UniqueConstraint(
                fields=["exam", "position"], name="Unique position"
            ),
            models.UniqueConstraint(
                fields=["exam", "exam_settings"], name="Unique state"
            ),
        ]
        ordering = ["exam", "position"]

    def natural_key(self):
        return (self.name, self.exam.natural_key())

    def __str__(self):
        return f"{self.name} {self.exam}"

    def apply(self):
        """ apply the settings to exam"""
        self.is_applicable(raise_errs=True)
        # Apply new settings
        new_settings = self.exam_settings
        for key, val in new_settings.items():
            setattr(self.exam, key, val)
        self.exam.save()

    def update_settings(self, new_settings):
        assert isinstance(new_settings, dict)
        assert set(new_settings.keys()) <= set(
            self.exam_settings.keys()
        ), "Keys of provided setting don't match available keys."
        self.exam_settings.update(new_settings)
        self.save()

    def is_current_state(self):
        current_settings = {
            k: getattr(self.exam, k) for k in self.get_available_exam_settings()
        }
        return self.exam_settings == current_settings

    def _check_warnings(self):
        warnings = []
        for check in self.checks_warning:
            func = getattr(state_checks, check)
            res = func(self.exam)
            if not res["passed"]:
                warnings.append(res)
        return warnings

    def _check_errors(self, raise_errs=False):
        errors = []
        for check in self.checks_error:
            func = getattr(state_checks, check)
            res = func(self.exam)
            if not res["passed"]:
                errors.append(res)
                if raise_errs:
                    raise ValueError(f"State {self.name} is blocked. {res['message']} ")
        return errors

    def run_checks(self):
        warnings = self._check_warnings()
        errors = self._check_errors()
        return {"warnings": warnings, "errors": errors}

    def is_applicable(self, raise_errs=False):
        return not bool(self._check_errors(raise_errs=raise_errs))

    def is_applicable_organizers(self):
        return self.is_applicable() and self.available_to_organizers

    def get_available_question_settings(self):
        return [
            s.name
            for s in get_selectable_question_fields()
            if s.name in self.available_question_settings
        ]

    @classmethod
    def get_current_state(cls, exam):
        current_settings = {
            k: getattr(exam, k) for k in cls.get_available_exam_settings()
        }
        # objects.filter(..).first() returns state or None, note that this filter provides a unique state
        current_state = cls.objects.filter(
            exam=exam, exam_settings=current_settings
        ).first()
        return current_state

    @classmethod
    def get_available_exam_settings(cls):
        return [f.name for f in get_available_exam_fields()]

    @classmethod
    def get_applicable_states(cls, exam, is_superuser=False):
        states = cls.objects.filter(exam=exam).all()
        res = []
        for state in states:
            if (
                state.is_applicable() and is_superuser
            ) or state.is_applicable_organizers():
                res.append(state)
        return res

    @staticmethod
    def get_available_checks():
        func_list = inspect.getmembers(state_checks, inspect.isfunction)
        return [(f[0], inspect.getdoc(f[1])) for f in func_list]

    @staticmethod
    def get_selectable_question_choices():
        available_fields = get_selectable_question_fields()
        choices = []
        for field in available_fields:
            if hasattr(field, "help_text"):
                choices.append([field.name, field.help_text])
            else:
                choices.append([field.name, field.name])
        return choices
