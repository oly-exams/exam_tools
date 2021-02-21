# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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
from collections import OrderedDict
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from ipho_exam.models import Exam, Question

import ipho_control.phase_checks as phase_checks


class ExamPhaseManager(models.Manager):
    def get_by_natural_key(self, name, exam):
        return self.get(name=name, exam=Exam.objects.get_by_natural_key(exam))


class ExamPhase(models.Model):
    objects = ExamPhaseManager()

    position = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField(help_text="A description shown to the organizers.")
    public_description = models.TextField(
        help_text="A description shown to all leaders and staff members."
    )

    before_switching = models.TextField(
        null=True,
        blank=True,
        help_text="Text displayed when confirming switching to this phase.",
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    available_to_organizers = models.BooleanField(
        default=True,
        help_text='Lets organizers with the "can_access_control" permission see and select this phase.',
    )

    exam_settings = models.JSONField(
        default=Exam.get_default_control_settings,
        help_text="A dictionary containing fields and settings.",
    )

    available_question_settings = models.JSONField(
        default=list,
        help_text="A list of question fields.",
        null=True,
        blank=True,
    )

    checks_warning = models.JSONField(
        default=list,
        help_text="A list of checks that can trigger a warning when applying the transition.",
        null=True,
        blank=True,
    )

    checks_error = models.JSONField(
        default=list,
        help_text="A list of checks that can prevent the transition.",
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
                fields=["exam", "exam_settings"], name="Unique phase"
            ),
        ]
        ordering = ["exam", "position"]

    def natural_key(self):
        return (self.name, self.exam.natural_key())

    def __str__(self):
        return f"{self.name} {self.exam}"

    def clean(self):
        if set(self.exam_settings.keys()) != set(self.get_available_exam_field_names()):
            raise ValidationError(
                f"Exam settings don't match available keys. Settings: {self.exam_settings}, Available: {self.get_available_exam_field_names()}",
                code="invalid",
            )

        setting_choices = self.get_available_exam_field_choices()
        for name, value in self.exam_settings.items():
            if name in setting_choices and not value in setting_choices[name]:
                raise ValidationError(
                    f"Value {value} for exam setting {name} is not available. Available choices are: {setting_choices}",
                    code="invalid",
                )

        controllable_q_fields = [f.name for f in Question.get_controllable_fields()]
        if not set(self.available_question_settings).issubset(
            set(controllable_q_fields)
        ):
            raise ValidationError(
                f"Question settings {self.available_question_settings} are not a subset of the controllable settings: {controllable_q_fields}",
                code="invalid",
            )
        checks = {c[0] for c in self.get_check_choices()}
        if not set(self.checks_warning).issubset(checks):
            raise ValidationError(
                f"Warning checks {self.checks_warning} are not a subset of the available checks: {checks}",
                code="invalid",
            )
        if not set(self.checks_error).issubset(checks):
            raise ValidationError(
                f"Error checks {self.checks_error} are not a subset of the available checks: {checks}",
                code="invalid",
            )

        double_checks = set(self.checks_error).intersection(set(self.checks_warning))
        if double_checks:
            raise ValidationError(
                f"Checks cannot be both warnings and errors. The following checks have been selected twice: {double_checks}.",
                code="invalid",
            )

    def apply(self, username=None):
        """Apply the settings to exam"""
        self.is_applicable(raise_errs=True)
        # Apply new settings
        new_settings = self.exam_settings
        for key, val in new_settings.items():
            setattr(self.exam, key, val)

        # create ExamPhaseHistory with username (which cannot be set on the post save)
        ex_hist = ExamPhaseHistory(
            exam=self.exam, to_settings=new_settings, to_phase=self
        )
        if username is not None:
            ex_hist.user = username
        ex_hist.save()
        try:
            # Save the exam, this will trigger the post save, which will not generate a new history
            self.exam.save()
        except:
            # Delete the history if something went wrong.
            ex_hist.delete()
            raise

    def is_current_phase(self):
        """Checks whether this phase is the current phase."""
        current_settings = {
            k: getattr(self.exam, k) for k in self.get_available_exam_field_names()
        }
        return self.exam_settings == current_settings

    def _check_warnings(self, return_all=False):
        """Evaluates all checks_warning, returns only failed checks per default."""
        warnings = []
        for check in self.checks_warning:
            func = getattr(phase_checks, check)
            res = func(self.exam)
            if not res["passed"] or return_all:
                res["name"] = check
                warnings.append(res)
        return warnings

    def _check_errors(self, raise_errs=False, return_all=False):
        """Evaluates all checks_warning, returns only failed checks per default, can raise errors if checks fail."""
        errors = []
        for check in self.checks_error:
            func = getattr(phase_checks, check)
            res = func(self.exam)
            if not res["passed"] or return_all:
                res["name"] = check
                errors.append(res)
                if raise_errs and not res["passed"]:
                    raise ValueError(f"Phase {self.name} is blocked. {res['message']} ")
        return errors

    def run_checks(self, return_all=False):
        """Runs all checks, returns only failed checks per default."""
        warnings = self._check_warnings(return_all=return_all)
        errors = self._check_errors(return_all=return_all)
        help_texts = dict(self.get_check_choices())
        return {"warnings": warnings, "errors": errors, "help_texts": help_texts}

    def is_applicable(self, raise_errs=False):
        """Checks whether this phase can be applied."""
        return not bool(self._check_errors(raise_errs=raise_errs))

    def is_applicable_organizers(self):
        """Checks whether this phase can be applied by organizers."""
        return self.is_applicable() and self.available_to_organizers

    def get_available_question_settings(self):
        """Returns question settings which can be changed in this phase."""
        return [
            s.name
            for s in Question.get_controllable_fields()
            if s.name in self.available_question_settings
        ]

    def get_ordered_settings(self):
        av_set = self.get_available_exam_field_names()
        return OrderedDict((s, self.exam_settings.get(s)) for s in av_set)

    @classmethod
    def get_current_phase(cls, exam):
        """Returns the current phase of exam, None if it doesn't exist."""
        current_settings = {
            k: getattr(exam, k) for k in cls.get_available_exam_field_names()
        }
        # objects.filter(..).first() returns phase or None, note that this filter provides a unique phase
        current_phase = cls.objects.filter(
            exam=exam, exam_settings=current_settings
        ).first()
        return current_phase

    @classmethod
    def get_available_exam_fields(cls):
        """Returns the exam fields which are available in in exam_settings."""
        return Exam.get_controllable_fields()

    @classmethod
    def get_available_exam_field_names(cls):
        """Returns the names of the exam fields which are available in in exam_settings."""
        return [f.name for f in cls.get_available_exam_fields()]

    @classmethod
    def get_available_exam_field_choices(cls):  # pylint: disable=invalid-name
        """Returns the names of the exam fields which are available in in exam_settings."""
        choices = {}
        for f in cls.get_available_exam_fields():
            if hasattr(f, "choices"):
                choices[f.name] = [c[0] for c in f.choices]
            elif f.get_internal_type() == "BooleanField":
                choices[f.name] = [True, False]

        return choices

    @classmethod
    def get_exam_field_help_texts(cls):
        """Returns a dictionary {field_name:help_text}."""
        res = {}
        for f in cls.get_available_exam_fields():
            if hasattr(f, "help_text"):
                res[f.name] = f.help_text
            else:
                res[f.name] = None
        return res

    @classmethod
    def get_exam_field_verbose_choices(cls):
        """"Returns a dictionary {field_name:choices}"""
        res = {}
        for f in cls.get_available_exam_fields():
            if hasattr(f, "choices"):
                res[f.name] = dict(f.choices)
        return res

    @classmethod
    def get_exam_field_verbose_names(cls):
        """"Returns a dictionary {field_name:verbose_name}"""
        res = {}
        for f in cls.get_available_exam_fields():
            if hasattr(f, "verbose_name"):
                res[f.name] = f.verbose_name
            else:
                res[f.name] = f.name
        return res

    @classmethod
    def get_applicable_phases(cls, exam, is_superuser=False):
        """Returns all phases which can be applied to exam."""
        phases = cls.objects.filter(exam=exam).all()
        res = []
        for phase in phases:
            if (
                phase.is_applicable() and is_superuser
            ) or phase.is_applicable_organizers():
                res.append(phase)
        return res

    @staticmethod
    def get_check_choices():
        """Returns a list of tuples [(check.name, check.docstring)], listing all available checks."""
        func_list = inspect.getmembers(phase_checks, inspect.isfunction)
        return [(f[0], inspect.getdoc(f[1])) for f in func_list]

    @staticmethod
    def get_question_setting_choices():
        """Returns a list of tuples [(question_setting.name, question_setting.help_text)], listing all question settings that can be set in available_question_settings."""
        available_fields = Question.get_controllable_fields()
        choices = []
        for field in available_fields:
            if hasattr(field, "help_text"):
                choices.append([field.name, field.help_text])
            else:
                choices.append([field.name, field.name])
        return choices


class ExamPhaseHistory(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    user = models.CharField(max_length=200, default="Some superuser")
    to_phase = models.ForeignKey(
        ExamPhase,
        on_delete=models.CASCADE,
        help_text="The phase to which the exam was changed (if applicable).",
        null=True,
        blank=True,
    )
    to_settings = models.JSONField(
        default=Exam.get_default_control_settings,
        help_text="The settings to which the exam was changed.",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_previous(self):
        """Returns the previous phase of self belonging to the same exam."""
        return (
            ExamPhaseHistory.objects.filter(
                timestamp__lt=self.timestamp, exam=self.exam
            )
            .order_by("-timestamp")
            .first()
        )

    def changed_to_previous(self):
        """Returns the exam phase changes to the previous phase."""
        res = {}
        previous = self.get_previous()
        if previous is None:
            return {}
        previous_settings = previous.to_settings
        for s in ExamPhase.get_available_exam_field_names():
            if self.to_settings.get(s) != previous_settings.get(s):
                changed = {
                    "new": self.to_settings.get(s),
                    "old": previous_settings.get(s),
                }
                res[s] = changed
        return res

    def unchanged_to_previous(self):
        """Returns the unchanged exam settings relative to the previous phase."""
        res = {}
        previous = self.get_previous()
        if previous is None:
            return self.to_settings
        previous_settings = previous.to_settings
        for s in ExamPhase.get_available_exam_field_names():
            if self.to_settings.get(s) == previous_settings.get(s):
                res[s] = self.to_settings.get(s)
        return res

    def get_ordered_to_settings(self):
        av_set = ExamPhase.get_available_exam_field_names()
        return OrderedDict((s, self.to_settings[s]) for s in av_set)

    @classmethod
    def get_latest(cls, exam):
        """Returns the latest phase of exam."""
        if cls.objects.filter(exam=exam).exists():
            return cls.objects.filter(exam=exam).latest("timestamp")
        return None

    class Meta:
        verbose_name_plural = "exam histories"
        ordering = ["-timestamp"]


@receiver(post_save, sender=Exam, dispatch_uid="create_exam_history_on_exam_change")
def create_actions_on_exam_creation(
    instance, created, raw, **kwargs
):  # pylint: disable=unused-argument
    """Creates an ExamPhaseHistory when exam settings are modified."""
    # Ignore fixtures.
    if raw:
        return
    current_settings = {
        k: getattr(instance, k) for k in ExamPhase.get_available_exam_field_names()
    }
    # Check whether there is a History with the same phase, if yes, abort.
    latest_history = ExamPhaseHistory.get_latest(instance)
    if latest_history is not None and latest_history.to_settings == current_settings:
        return

    ex_hist = ExamPhaseHistory(to_settings=current_settings, exam=instance)
    ex_hist.to_phase = ExamPhase.get_current_phase(instance)
    ex_hist.save()
