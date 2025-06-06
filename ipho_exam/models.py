# pylint: disable=too-many-lines, consider-using-f-string

# mskoenz: text_direction on 738 inactive, is this intended?
#         disabled Document.question_name, since it makes no sense

import codecs
import os
import subprocess
import time
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel

import ipho_exam
from ipho_core.models import Delegation, Student
from ipho_exam import fonts

from .exceptions import IphoExamForbidden
from .utils import natural_id

OFFICIAL_DELEGATION = getattr(settings, "OFFICIAL_DELEGATION")
SITE_URL = getattr(settings, "SITE_URL")
INKSCAPE_BIN = getattr(settings, "INKSCAPE_BIN", "inkscape")


class LanguageManager(models.Manager):
    def get_by_natural_key(self, name, delegation_name):
        return self.get(
            name=name, delegation=Delegation.objects.get_by_natural_key(delegation_name)
        )


class Language(models.Model):
    objects = LanguageManager()
    DIRECTION_CHOICES = (("ltr", "Left-to-right"), ("rtl", "Right-to-left"))
    POLYGLOSSIA_CHOICES = (
        ("afrikaans", "Afrikaans"),
        ("albanian", "Albanian"),
        ("amharic", "Amharic"),
        ("arabic", "Arabic"),
        ("armenian", "Armenian"),
        ("asturian", "Asturian"),
        ("basque", "Basque"),
        ("belarusian", "Belarusian"),
        ("bengali", "Bengali"),
        ("bosnian", "Bosnian"),
        ("breton", "Breton"),
        ("bulgarian", "Bulgarian"),
        ("catalan", "Catalan"),
        ("coptic", "Coptic"),
        ("croatian", "Croatian"),
        ("czech", "Czech"),
        ("danish", "Danish"),
        ("divehi", "Divehi"),
        ("dutch", "Dutch"),
        ("english", "English"),
        ("esperanto", "Esperanto"),
        ("estonian", "Estonian"),
        ("finnish", "Finnish"),
        ("french", "French"),
        ("friulian", "Friulian"),
        ("gaelic", "Gaelic"),
        ("galician", "Galician"),
        ("georgian", "Georgian"),
        ("german", "German"),
        ("greek", "Greek"),
        ("hebrew", "Hebrew"),
        ("hindi", "Hindi"),
        ("hungarian", "Hungarian"),
        ("icelandic", "Icelandic"),
        ("interlingua", "Interlingua"),
        ("italian", "Italian"),
        ("japanese", "Japanese"),
        ("kannada", "Kannada"),
        ("khmer", "Khmer"),
        ("korean", "Korean"),
        ("kurdish", "Kurdish"),
        ("lao", "Lao"),
        ("latin", "Latin"),
        ("latvian", "Latvian"),
        ("lithuanian", "Lithuanian"),
        ("macedonian", "Macedonian"),
        ("malay", "Malay"),
        ("malayalam", "Malayalam"),
        ("marathi", "Marathi"),
        ("mongolian", "Mongolian"),
        ("myanmar", "Myanmar"),
        ("nko", "Nko"),
        ("norwegian", "Norwegian"),
        ("occitan", "Occitan"),
        ("persian", "Persian"),
        ("piedmontese", "Piedmontese"),
        ("polish", "Polish"),
        ("portuguese", "Portuguese"),
        ("romanian", "Romanian"),
        ("romansh", "Romansh"),
        ("russian", "Russian"),
        ("sami", "Sami"),
        ("sanskrit", "Sanskrit"),
        ("serbian", "Serbian"),
        ("slovak", "Slovak"),
        ("slovenian", "Slovenian"),
        ("sorbian", "Sorbian"),
        ("spanish", "Spanish"),
        ("swedish", "Swedish"),
        ("syriac", "Syriac"),
        ("tamil", "Tamil"),
        ("telugu", "Telugu"),
        ("thai", "Thai"),
        ("tibetan", "Tibetan"),
        ("turkish", "Turkish"),
        ("turkmen", "Turkmen"),
        ("ukrainian", "Ukrainian"),
        ("urdu", "Urdu"),
        ("uyghur", "Uyghur"),
        ("vietnamese", "Vietnamese"),
        ("welsh", "Welsh"),
    )
    STYLES_CHOICES = (
        ("afrikaans", "Afrikaans"),
        ("albanian", "Albanian"),
        ("amharic", "Amharic"),
        ("arabic", "Arabic"),
        ("armenian", "Armenian"),
        ("asturian", "Asturian"),
        ("azerbaijani", "Azerbaijani"),
        ("basque", "Basque"),
        ("belarusian", "Belarusian"),
        ("bengali", "Bengali"),
        ("bosnian", "Bosnian"),
        ("breton", "Breton"),
        ("bulgarian", "Bulgarian"),
        ("burmese", "Burmese"),
        ("cantonese", "Cantonese"),
        ("catalan", "Catalan"),
        ("chinese", "Chinese (simplified)"),
        ("chinese_tc", "Chinese (traditional)"),
        ("coptic", "Coptic"),
        ("croatian", "Croatian"),
        ("czech", "Czech"),
        ("danish", "Danish"),
        ("divehi", "Divehi"),
        ("dutch", "Dutch"),
        ("english", "English"),
        ("esperanto", "Esperanto"),
        ("estonian", "Estonian"),
        ("filipino", "Filipino"),
        ("finnish", "Finnish"),
        ("french", "French"),
        ("friulian", "Friulian"),
        ("galician", "Galician"),
        ("georgian", "Georgian"),
        ("german", "German"),
        ("greek", "Greek"),
        ("hebrew", "Hebrew"),
        ("hindi", "Hindi"),
        ("hungarian", "Hungarian"),
        ("icelandic", "Icelandic"),
        ("indonesian", "Indonesian"),
        ("interlingua", "Interlingua"),
        ("irish", "Irish"),
        ("italian", "Italian"),
        ("japanese", "Japanese"),
        ("kannada", "Kannada"),
        ("kazakh", "Kazakh"),
        ("khmer", "Khmer"),
        ("korean", "Korean"),
        ("kurdish", "Kurdish"),
        ("kyrgyz", "Kyrgyz"),
        ("lao", "Lao"),
        ("latin", "Latin"),
        ("latvian", "Latvian"),
        ("lithuanian", "Lithuanian"),
        ("luxembourgish", "Luxembourgish"),
        ("macedonian", "Macedonian"),
        ("magyar", "Magyar"),
        ("malay", "Malay"),
        ("malayalam", "Malayalam"),
        ("malaysian", "Malaysian"),
        ("mandarin", "Mandarin"),
        ("marathi", "Marathi"),
        ("mongolian", "Mongolian"),
        ("montenegrin", "Montenegrin"),
        ("nepali", "Nepali"),
        ("northern sotho", "Northern Sotho"),
        ("norwegian bokmål", "Norwegian Bokmål"),
        ("norwegian nynorsk", "Norwegian Nynorsk"),
        ("occitan", "Occitan"),
        ("persian", "Persian"),
        ("piedmontese", "Piedmontese"),
        ("polish", "Polish"),
        ("portuguese", "Portuguese"),
        ("romanian", "Romanian"),
        ("romansh", "Romansh"),
        ("russian", "Russian"),
        ("sanskrit", "Sanskrit"),
        ("scottish", "Scottish"),
        ("serbian", "Serbian"),
        ("sinhalese", "Sinhalese"),
        ("slovak", "Slovak"),
        ("slovenian", "Slovenian"),
        ("southern ndebele", "Southern Ndebele"),
        ("southern sotho", "Southern Sotho"),
        ("spanish", "Spanish"),
        ("swedish", "Swedish"),
        ("syriac", "Syriac"),
        ("tajik", "Tajik"),
        ("tamil", "Tamil"),
        ("telugu", "Telugu"),
        ("thai", "Thai"),
        ("tibetan", "Tibetan"),
        ("tsonga", "Tsonga"),
        ("tswana", "Tswana"),
        ("turkish", "Turkish"),
        ("turkmen", "Turkmen"),
        ("ukrainian", "Ukrainian"),
        ("urdu", "Urdu"),
        ("uzbek", "Uzbek"),
        ("venda", "Venda"),
        ("vietnamese", "Vietnamese"),
        ("welsh", "Welsh"),
        ("xhosa", "Xhosa"),
        ("zulu", "Zulu"),
    )

    name = models.CharField(max_length=100, db_index=True)
    delegation = models.ForeignKey(
        Delegation, blank=True, null=True, on_delete=models.CASCADE
    )
    hidden = models.BooleanField(default=False)
    hidden_from_submission = models.BooleanField(default=False)
    versioned = models.BooleanField(default=False)
    is_pdf = models.BooleanField(default=False)
    style = models.CharField(
        max_length=200, blank=True, null=True, choices=STYLES_CHOICES
    )
    direction = models.CharField(max_length=3, default="ltr", choices=DIRECTION_CHOICES)
    polyglossia = models.CharField(
        max_length=100, default="english", choices=POLYGLOSSIA_CHOICES
    )
    polyglossia_options = models.TextField(blank=True, null=True)
    font = models.CharField(
        max_length=100,
        default="notosans",
        choices=[(k, v["font"]) for k, v in sorted(fonts.ipho.items())],
    )
    extraheader = models.TextField(blank=True)

    class Meta:
        unique_together = index_together = (("name", "delegation"),)
        ordering = ["delegation", "name"]

    def natural_key(self):
        return (self.name,) + self.delegation.natural_key()

    def __str__(self):
        return f"{self.name} ({self.delegation.country})"

    def check_permission(self, user):
        if user.is_superuser:
            return True

        return user.delegation_set.filter(id=self.delegation.pk).exists()

    def is_official(self):
        return self.delegation.name == OFFICIAL_DELEGATION

    @classmethod
    def get_official(cls):
        return cls.objects.get(delegation__name=OFFICIAL_DELEGATION)


class ExamManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

    def for_user(self, user):
        queryset = self.get_queryset()
        if user.is_superuser:
            return queryset.filter(visibility__gte=Exam.VISIBLE_2ND_LVL_SUPPORT_ONLY)

        is_official_delegation_member = Delegation.objects.filter(
            members=user, name=OFFICIAL_DELEGATION
        ).exists()
        if (
            user.has_perm("ipho_core.is_organizer_admin")
            or user.has_perm("ipho_core.can_edit_exam")
            or (
                user.has_perm("ipho_core.is_delegation")
                and is_official_delegation_member
            )
        ):
            return queryset.filter(
                visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT
            )
        if (
            user.has_perm("ipho_core.can_see_boardmeeting")
            or user.has_perm("ipho_core.is_marker")
            or user.has_perm("ipho_core.is_printstaff")
        ):
            return queryset.filter(
                visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING
            )
        if user.has_perm("ipho_core.is_delegation_print"):
            delegation = Delegation.objects.filter(members=user)
            actions = ExamAction.objects.filter(
                delegation__in=delegation,
                action=ExamAction.TRANSLATION,
                status=ExamAction.SUBMITTED,
            )
            return (
                queryset.filter(
                    visibility__gte=Exam.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING,
                    delegation_status__in=actions,
                )
                .filter(
                    Q(
                        answer_sheet_scan_upload__gte=Exam.ANSWER_SHEET_SCAN_UPLOAD_STUDENT_ANSWER
                    )
                    | Q(
                        submission_printing__gte=Exam.SUBMISSION_PRINTING_WHEN_SUBMITTED
                    ),
                )
                .distinct()
            )
        return self.none()


class Exam(models.Model):
    objects = ExamManager()

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=100, unique=True)

    has_solution = models.BooleanField(default=False)

    FLAG_SQUASHED = 1

    flags = models.PositiveSmallIntegerField(default=0)

    # pylint: disable=invalid-name

    # Note that IntegerFields enable us to filter using order relations.
    # We mostly use >=/__gte to filter the hierarchical flags
    # e.g. visibility__gte=Orga+2nd_level shows the exam when the visibility
    # is set to orgas+2nd_level or orgas+2nd_level+boardmeeting
    #
    # Note also, that the colors in the cockpit depend on the number:
    # <0: Grey, ==0: Blue, >0: Yellow

    VISIBLE_2ND_LVL_SUPPORT_ONLY = -1
    VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT = 0
    VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING = 1

    VISIBILITY_CHOICES = (
        (VISIBLE_2ND_LVL_SUPPORT_ONLY, "2nd level support only"),
        (VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT, "Organizer + 2nd level support"),
        (
            VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING,
            "Boardmeeting + Organizer + 2nd level support",
        ),
    )

    # See comments on IntegerFields above
    visibility = models.IntegerField(
        default=0,
        choices=VISIBILITY_CHOICES,
        help_text="Sets the visibility of the exam for organizers and delegations.",
        verbose_name="Exam Visibility",
    )

    CAN_PUBLISH_NOBODY = -1
    CAN_PUBLISH_ORGANIZER = 0

    CAN_PUBLISH_CHOICES = (
        (CAN_PUBLISH_NOBODY, "Nobody"),
        (CAN_PUBLISH_ORGANIZER, "Organizers"),
    )

    # See comments on IntegerFields above
    can_publish = models.IntegerField(
        default=0,
        choices=CAN_PUBLISH_CHOICES,
        help_text="Sets the ability to publish new versions of the exam for organizers.",
        verbose_name="Can Publish",
    )

    CAN_TRANSLATE_NOBODY = -1
    CAN_TRANSLATE_ORGANIZER = 0
    CAN_TRANSLATE_BOARDMEETING = 1

    CAN_TRANSLATE_CHOICES = (
        (CAN_TRANSLATE_NOBODY, "Nobody"),
        (CAN_TRANSLATE_ORGANIZER, "Organizer only"),
        (CAN_TRANSLATE_BOARDMEETING, "Boardmeeting members + organizers"),
    )

    # See comments on IntegerFields above
    can_translate = models.IntegerField(
        default=-1,
        choices=CAN_TRANSLATE_CHOICES,
        help_text="Sets the ability to translate for organizers and delegations.",
        verbose_name="Can Translate",
    )

    FEEDBACK_READONLY = 0
    FEEDBACK_CAN_BE_OPENED = 1
    FEEDBACK_INVISIBLE = -1

    FEEDBACK_CHOICES = (
        (FEEDBACK_READONLY, "Read only"),
        (FEEDBACK_CAN_BE_OPENED, "Can be opened"),
        (FEEDBACK_INVISIBLE, "Invisible"),
    )

    # See comments on IntegerFields above
    feedback = models.IntegerField(
        default=0,
        choices=FEEDBACK_CHOICES,
        help_text="Sets the status of the feedbacks for all questions.",
        verbose_name="Feedback",
    )

    CAN_SUBMIT_NO = -1
    CAN_SUBMIT_YES = 1

    CAN_SUBMIT_CHOICES = (
        (CAN_SUBMIT_NO, "No"),
        (CAN_SUBMIT_YES, "Yes"),
    )

    # See comments on IntegerFields above
    can_submit = models.IntegerField(
        default=-1,
        choices=CAN_SUBMIT_CHOICES,
        help_text="Sets the ability to do a final submission for delegations.",
        verbose_name="Can Submit",
    )

    SUBMISSION_PRINTING_NOT_VISIBLE = -1
    SUBMISSION_PRINTING_WHEN_SUBMITTED = 0

    SUBMISSION_PRINTING_CHOICES = (
        (SUBMISSION_PRINTING_NOT_VISIBLE, "No, not visible"),
        (SUBMISSION_PRINTING_WHEN_SUBMITTED, "When submitted"),
    )

    # See comments on IntegerFields above
    submission_printing = models.IntegerField(
        default=-1,
        choices=SUBMISSION_PRINTING_CHOICES,
        help_text="Sets the ability to print the exam.",
        verbose_name="Submission Printing",
    )

    ANSWER_SHEET_SCAN_UPLOAD_NOT_POSSIBLE = -1
    ANSWER_SHEET_SCAN_UPLOAD_STUDENT_ANSWER = 0

    ANSWER_SHEET_SCAN_UPLOAD_CHOICES = (
        (ANSWER_SHEET_SCAN_UPLOAD_NOT_POSSIBLE, "Not possible"),
        (ANSWER_SHEET_SCAN_UPLOAD_STUDENT_ANSWER, "Participant answer"),
    )

    # See comments on IntegerFields above
    answer_sheet_scan_upload = models.IntegerField(
        default=-1,
        choices=ANSWER_SHEET_SCAN_UPLOAD_CHOICES,
        help_text="Sets the ability for scans being uploaded via the web interface.",
        verbose_name="Answer Sheet Manual Scan Upload",
    )

    DELEGATION_SCAN_ACCESS_NO = -1
    DELEGATION_SCAN_ACCESS_STUDENT_ANSWER = 0

    DELEGATION_SCAN_ACCESS_CHOICES = (
        (DELEGATION_SCAN_ACCESS_NO, "No"),
        (DELEGATION_SCAN_ACCESS_STUDENT_ANSWER, "Participant answer"),
    )

    # See comments on IntegerFields above
    delegation_scan_access = models.IntegerField(
        default=-1,
        choices=DELEGATION_SCAN_ACCESS_CHOICES,
        help_text="Sets the access to the scanned exams for delegations.",
        verbose_name="Delegation Scan Access",
    )

    MARKING_ORGANIZER_VIEW_MODERATION_FINAL = -1
    MARKING_ORGANIZER_VIEW_WHEN_SUBMITTED = 0

    MARKING_ORGANIZER_VIEW_CHOICES = (
        (
            MARKING_ORGANIZER_VIEW_MODERATION_FINAL,
            "In moderation and when marks are finalized",
        ),
        (
            MARKING_ORGANIZER_VIEW_WHEN_SUBMITTED,
            "When the delegation has submitted their marks",
        ),
    )

    # See comments on IntegerFields above
    marking_organizer_can_see_delegation_marks = models.IntegerField(
        default=-1,
        choices=MARKING_ORGANIZER_VIEW_CHOICES,
        help_text="Sets the access of organizers to the delegation marks",
        verbose_name="Organizer can see delegation marks",
    )

    MARKING_DELEGATION_VIEW_NO = -1
    MARKING_DELEGATION_VIEW_WHEN_SUBMITTED = 0
    MARKING_DELEGATION_VIEW_YES = 1

    MARKING_DELEGATION_VIEW_CHOICES = (
        (MARKING_DELEGATION_VIEW_NO, "No"),
        (
            MARKING_DELEGATION_VIEW_WHEN_SUBMITTED,
            "When the delegation has submitted their marks",
        ),
        (MARKING_DELEGATION_VIEW_YES, "Yes"),
    )

    # See comments on IntegerFields above
    marking_delegation_can_see_organizer_marks = models.IntegerField(
        default=-1,
        choices=MARKING_DELEGATION_VIEW_CHOICES,
        help_text="Sets the access of delegations to the organizer marks",
        verbose_name="Delegations can see organizer marks",
    )

    MARKING_ORGANIZER_CAN_ENTER_NOTHING = -1
    MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED = 0
    MARKING_ORGANIZER_CAN_ENTER_IF_NOT_FINAL = 1

    MARKING_ORGANIZER_CAN_ENTER_CHOICES = (
        (MARKING_ORGANIZER_CAN_ENTER_NOTHING, "No"),
        (
            MARKING_ORGANIZER_CAN_ENTER_IF_NOT_SUBMITTED,
            "If delegation has not submitted marks",
        ),
        (MARKING_ORGANIZER_CAN_ENTER_IF_NOT_FINAL, "If marks are not finalized"),
    )

    # See comments on IntegerFields above
    marking_organizer_can_enter = models.IntegerField(
        default=-1,
        choices=MARKING_ORGANIZER_CAN_ENTER_CHOICES,
        help_text="Sets the ability of markers to edit marks.",
        verbose_name="Organizers can edit marks",
    )

    MARKING_DELEGATION_ACTION_NOTHING = -1
    MARKING_DELEGATION_ACTION_ENTER_SUBMIT = 0
    MARKING_DELEGATION_ACTION_ENTER_SUBMIT_FINALIZE = 1

    MARKING_DELEGATION_ACTION_CHOICES = (
        (MARKING_DELEGATION_ACTION_NOTHING, "Nothing"),
        (MARKING_DELEGATION_ACTION_ENTER_SUBMIT, "Can enter and submit marks"),
        (
            MARKING_DELEGATION_ACTION_ENTER_SUBMIT_FINALIZE,
            "Can enter, submit and finalize marks",
        ),
    )

    # See comments on IntegerFields above
    marking_delegation_action = models.IntegerField(
        default=-1,
        choices=MARKING_DELEGATION_ACTION_CHOICES,
        help_text="Sets the ability of delegations to enter, submit and finalize their marks.",
        verbose_name="Delegation marking actions",
    )

    MODERATION_CLOSED = -1
    MODERATION_OPEN = 0

    MODERATION_CHOICES = (
        (MODERATION_CLOSED, "Not open"),
        (MODERATION_OPEN, "Can be moderated"),
    )

    # See comments on IntegerFields above
    moderation = models.IntegerField(
        default=-1,
        choices=MODERATION_CHOICES,
        help_text="Allow access to moderation interface.",
        verbose_name="Moderation",
    )

    # Fields controllable by the control app
    # NOTE: only fields having a default value are respected.
    _controllable_fields = [
        "visibility",
        "can_publish",
        "can_translate",
        "can_submit",
        "feedback",
        "submission_printing",
        "answer_sheet_scan_upload",
        "delegation_scan_access",
        "marking_organizer_can_see_delegation_marks",
        "marking_organizer_can_enter",
        "marking_delegation_can_see_organizer_marks",
        "marking_delegation_action",
        "moderation",
    ]

    def __str__(self):
        return "%s" % (self.name)

    def natural_key(self):
        return (self.name,)

    class Meta:
        ordering = ["code", "name"]

    @classmethod
    def get_controllable_fields(cls):
        """Returns the fields available to the control app (i.e. changeable in ExamPhase)."""
        all_fields = cls._meta.get_fields()
        # controllable fields need to have a default value
        available_fields = [
            field
            for field in all_fields
            if field.name in cls._controllable_fields
            and hasattr(field, "default")
            and field.default is not models.fields.NOT_PROVIDED
        ]
        # use the ordering defined in controllable fields
        available_fields.sort(key=lambda o: cls._controllable_fields.index(o.name))
        return available_fields

    @classmethod
    def get_default_control_settings(cls):
        """Returns the default values for controllable fields."""
        available_fields = cls.get_controllable_fields()
        default_settings = {f.name: f.default for f in available_fields}
        return default_settings

    @classmethod
    def get_publishability(cls, user):
        if user.is_superuser:
            return cls.CAN_PUBLISH_NOBODY
        if user.has_perm("ipho_core.is_organizer_admin") or user.has_perm(
            "ipho_core.can_edit_exam"
        ):
            return cls.CAN_PUBLISH_ORGANIZER

        max_choice = max(
            choice[0] for choice in cls._meta.get_field("can_publish").choices
        )
        return max_choice + 1

    @classmethod
    def get_visibility(cls, user):
        if user.is_superuser:
            return cls.VISIBLE_2ND_LVL_SUPPORT_ONLY
        if user.has_perm("ipho_core.is_organizer_admin") or user.has_perm(
            "ipho_core.can_edit_exam"
        ):
            return cls.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT
        if (
            user.has_perm("ipho_core.can_see_boardmeeting")
            or user.has_perm("ipho_core.is_marker")
            or user.has_perm("ipho_core.is_printstaff")
        ):
            return cls.VISIBLE_ORGANIZER_AND_2ND_LVL_SUPPORT_AND_BOARDMEETING
        max_choice = max(
            choice[0] for choice in cls._meta.get_field("visibility").choices
        )
        return max_choice + 1

    @classmethod
    def get_translatability(cls, user):
        if (
            user.is_superuser
            or user.has_perm("ipho_core.is_organizer_admin")
            or user.has_perm("ipho_core.can_edit_exam")
        ):
            return Exam.CAN_TRANSLATE_ORGANIZER
        if user.has_perm("ipho_core.can_see_boardmeeting"):
            return Exam.CAN_TRANSLATE_BOARDMEETING
        max_choice = max(
            choice[0] for choice in cls._meta.get_field("can_translate").choices
        )
        return max_choice + 1

    @classmethod
    def get_submittability(cls, user):
        if user.has_perm("ipho_core.can_see_boardmeeting"):
            return Exam.CAN_SUBMIT_YES
        max_choice = max(
            choice[0] for choice in cls._meta.get_field("can_submit").choices
        )
        return max_choice + 1

    def check_visibility(self, user):
        return self.visibility >= Exam.get_visibility(user)

    def check_publishability(self, user):
        if not self.check_visibility(user):
            return False
        return self.can_publish >= Exam.get_publishability(user)

    def check_translatability(self, user):
        if not self.check_visibility(user):
            return False
        return self.can_translate >= Exam.get_translatability(user)

    def check_submittability(self, user):
        if not self.check_visibility(user):
            return False
        return self.can_submit >= Exam.get_submittability(user)

    def check_feedback_visible(self):
        return self.feedback >= Exam.FEEDBACK_READONLY

    def check_feedback_editable(self):
        return self.feedback >= Exam.FEEDBACK_CAN_BE_OPENED

    def delegation_can_submit_marking(self):
        return (
            self.marking_delegation_action
            >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT
        )

    def delegation_can_finalize_marking(self):
        return (
            self.marking_delegation_action
            >= Exam.MARKING_DELEGATION_ACTION_ENTER_SUBMIT_FINALIZE
        )

    def save(self, *args, **kwargs):
        if self.pk:
            previous_feedback = Exam.objects.get(pk=self.pk).feedback
        else:
            previous_feedback = None
        super().save(*args, **kwargs)

        if self.feedback != previous_feedback:
            for question in self.question_set.all():
                question.feedback_status = Question.FEEDBACK_CLOSED
                question.save()


class ParticipantManager(models.Manager):
    def get_by_natural_key(self, code, exam_key):
        return self.get(code=code, exam=Exam.objects.get_by_natural_key(*exam_key))


class Participant(models.Model):
    objects = ParticipantManager()

    code = models.CharField(max_length=10)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200 + 200)
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

    class Meta:
        unique_together = index_together = (("code", "exam"),)
        ordering = ["code", "exam"]

    def natural_key(self):
        return (self.code, self.exam.natural_key())

    def __str__(self):
        return f"{self.code} ({self.exam.name})"

    @property
    def is_group(self):
        return len(self.students.all()) > 1


@receiver(post_save, sender=Student, dispatch_uid="create_ppnt_on_stud_creation")
def create_ppnt_on_stud_creation(instance, created, raw, **kwargs):
    if raw:
        return
    for exam in Exam.objects.all():
        if created:
            _create_ppnt_on_creation_helper(exam, instance)
        else:
            for ppnt in instance.participant_set.all():
                if not ppnt.is_group:
                    ppnt.code = instance.code
                    ppnt.full_name = instance.full_name
                    ppnt.delegation = instance.delegation
                    ppnt.save()


def get_ppnt_on_stud_exam(exam, student):
    """creates a participant based on an exam and a student
    without storing it into the database.

    Args:
        exam (ipho_exam.models.Exam): exam
        student (ipho_exam.models.Student): student

    Returns:
        ipho_exam.models.Participant: participant
    """
    return Participant(
        code=student.code,
        exam=exam,
        full_name=student.full_name,
        delegation=student.delegation,
    )


@receiver(post_save, sender=Exam, dispatch_uid="create_ppnt_on_exam_creation")
def create_ppnt_on_exam_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    # the order is only important for for ci/cypress testing
    for student in Student.objects.order_by("pk"):
        _create_ppnt_on_creation_helper(instance, student)


def _create_ppnt_on_creation_helper(exam, student):
    ppnt, _ = Participant.objects.get_or_create(
        code=student.code,
        exam=exam,
        full_name=student.full_name,
        delegation=student.delegation,
    )
    ppnt.students.set((student,))


class QuestionManager(models.Manager):
    def get_by_natural_key(self, name, exam_name):
        return self.get(name=name, exam=Exam.objects.get_by_natural_key(exam_name))

    def for_user(self, user):
        return self.get_queryset().filter(exam__in=Exam.objects.for_user(user))


class Question(models.Model):
    objects = QuestionManager()

    CODE_TYPES = (
        ("Q", "Q (Question)"),
        ("A", "A (Answer)"),
        ("G", "G (General)"),
    )

    QUESTION = 0
    ANSWER = 1
    QUESTION_TYPES = (
        (QUESTION, "Question"),
        (ANSWER, "Answer"),
    )

    code = models.CharField(choices=CODE_TYPES, max_length=20, default="Q")
    name = models.CharField(max_length=100, db_index=True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(
        help_text="Sorting index inside one exam"
    )
    type = models.PositiveSmallIntegerField(choices=QUESTION_TYPES, default=QUESTION)

    FLAG_HIDDEN_PDF = 1

    flags = models.PositiveSmallIntegerField(default=0)

    FEEDBACK_CLOSED = -1
    FEEDBACK_ORGANIZER_COMMENT = 0
    FEEDBACK_EVERYBODY_COMMENT = 1
    FEEDBACK_OPEN = 2

    FEEDBACK_CHOICES = (
        (FEEDBACK_OPEN, "Open"),
        (
            FEEDBACK_EVERYBODY_COMMENT,
            "Feedbback entry closed, Everybody can comment, like & withdraw.",
        ),
        (FEEDBACK_ORGANIZER_COMMENT, "Feedbback entry closed, Organizer can comment."),
        (FEEDBACK_CLOSED, "Feedbback entry closed"),
    )

    feedback_status = models.IntegerField(
        default=-1,
        choices=FEEDBACK_CHOICES,
        help_text="Sets the status of the feedbacks for this questions.",
        verbose_name="Feedback",
    )

    working_pages = models.PositiveSmallIntegerField(
        default=0, help_text="How many pages for working sheets"
    )

    # Fields controllable by the control app
    _controllable_fields = [
        "feedback_status",
    ]

    ## TODO: add template field

    class Meta:
        ordering = ["exam", "position", "type", "code"]

    def is_answer_sheet(self):
        return self.type == self.ANSWER

    def is_question_sheet(self):
        return self.type == self.QUESTION

    def exam_name(self):
        return self.exam.name

    def __str__(self):
        return f"{self.name} [#{self.position} in {self.exam.name}]"

    def natural_key(self):
        return (self.name,) + self.exam.natural_key()

    natural_key.dependencies = ["ipho_exam.exam"]

    def has_published_version(self):
        return self.versionnode_set.filter(status="C").exists()

    def check_visibility(self, user):
        return self.exam.check_visibility(user)

    def check_feedback_visible(self):
        return self.exam.check_feedback_visible()

    def check_feedback_editable(self):
        editable = self.feedback_status == Question.FEEDBACK_OPEN
        return (
            self.check_feedback_visible()
            and self.exam.check_feedback_editable()
            and editable
        )

    def check_feedback_commentable(self):
        commentable = self.feedback_status >= Question.FEEDBACK_ORGANIZER_COMMENT
        return (
            self.check_feedback_visible()
            and self.exam.check_feedback_editable()
            and commentable
        )

    @classmethod
    def get_controllable_fields(cls):
        """Returns the fields available to the control app."""
        all_fields = cls._meta.get_fields()
        available_fields = [
            field for field in all_fields if field.name in cls._controllable_fields
        ]
        available_fields.sort(key=lambda o: o.name)
        return available_fields


class VersionNodeManager(models.Manager):
    def get_by_natural_key(
        self, version, question_name, exam_name, lang_name, delegation_name
    ):
        return self.get(
            version=version,
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name),
        )


class VersionNode(models.Model):
    objects = VersionNodeManager()
    STATUS_CHOICES = (
        ("P", "Proposal"),
        ("S", "Staged"),
        ("C", "Confirmed"),
    )

    text = models.TextField()
    ids_in_order = models.TextField(default="")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    version = models.IntegerField()
    tag = models.CharField(
        max_length=100, null=True, blank=True, help_text="leave empty to show no tag"
    )
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = index_together = (("question", "language", "version"),)
        ordering = ["question", "language", "-version", "-timestamp"]

    def question_name(self):
        return self.question.name

    def __str__(self):
        return "vnode: {} [{}, v{} {}, {}] - {}".format(
            self.question.name,
            self.language,
            self.version,
            self.tag,
            self.timestamp,
            self.status,
        )

    def natural_key(self):
        return (
            (self.version,) + self.question.natural_key() + self.language.natural_key()
        )

    natural_key.dependencies = ["ipho_exam.question", "ipho_exam.language"]


class TranslationNodeManager(models.Manager):
    def get_by_natural_key(self, question_name, exam_name, lang_name, delegation_name):
        return self.get(
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name),
        )


class TranslationNode(models.Model):
    objects = TranslationNodeManager()
    STATUS_CHOICES = (
        ("O", "In progress"),
        ("L", "Locked"),
        ("S", "Submitted"),
    )

    text = models.TextField(blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="O")
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = index_together = (("question", "language"),)
        ordering = ["question", "language", "-timestamp"]

    def question_name(self):
        return self.question.name

    def __str__(self):
        return f"node: {self.question.name} [{self.language}, {self.timestamp}] - {self.status}"

    def natural_key(self):
        return self.question.natural_key() + self.language.natural_key()

    natural_key.dependencies = ["ipho_exam.question", "ipho_exam.language"]


class AttributeChangeManager(models.Manager):
    def get_by_natural_key(self, *args, **kwargs):
        return self.get(
            node=TranslationNode.objects.get_by_natural_key(*args, **kwargs)
        )


class AttributeChange(models.Model):
    objects = AttributeChangeManager()
    content = models.TextField(blank=True)
    node = models.OneToOneField(TranslationNode, on_delete=models.CASCADE)

    def __str__(self):
        return f"attrs:{self.node}"

    def natural_key(self):
        return self.node.natural_key()

    natural_key.dependencies = [
        "ipho_exam.translationnode",
    ]


class PDFNodeManager(models.Manager):
    def get_by_natural_key(self, question_name, exam_name, lang_name, delegation_name):
        return self.get(
            language=Language.objects.get_by_natural_key(lang_name, delegation_name),
            question=Question.objects.get_by_natural_key(question_name, exam_name),
        )


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join(
        f"pdfnodes/Lang{instance.question.pk}Q{instance.language.pk}", filename
    )


class PDFNode(models.Model):
    objects = PDFNodeManager()
    STATUS_CHOICES = (
        ("O", "In progress"),
        ("L", "Locked"),
        ("S", "Submitted"),
    )

    pdf = models.FileField(upload_to=get_file_path, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="O")
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = index_together = (("question", "language"),)

    def question_name(self):
        return self.question.name

    def __str__(self):
        return f"pdfNode: {self.question.name} [{self.language}, {self.timestamp}] - {self.status}"

    def natural_key(self):
        return self.question.natural_key() + self.language.natural_key()

    natural_key.dependencies = ["ipho_exam.question", "ipho_exam.language"]


class TranslationImportTmp(models.Model):
    slug = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.slug} - {self.question}, {self.language}"


class CachedAutoTranslation(models.Model):
    source_and_lang_hash = models.CharField(max_length=32, primary_key=True)
    source_length = models.IntegerField()
    source_lang = models.CharField(max_length=5)
    target_lang = models.CharField(max_length=5)
    target_text = models.TextField(blank=True)
    hits = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.source_lang} -> {self.target_lang} ({self.source_length})"


class CachedHTMLDiff(models.Model):
    source_node = models.ForeignKey(
        VersionNode, on_delete=models.CASCADE, related_name="cached_diff_source"
    )
    target_node = models.ForeignKey(
        VersionNode, on_delete=models.CASCADE, related_name="cached_diff_target"
    )
    source_text = models.TextField()
    target_text = models.TextField()
    diff_text = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    timing = models.IntegerField(
        default=0, help_text="execution time of the diff in ms"
    )
    hits = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.source_node} -> {self.target_node}"

    class Meta:
        ordering = ["-hits", "-timestamp"]

    @staticmethod
    def calc_or_get_cache(source_node, target_node, diff_q):
        diff = CachedHTMLDiff.objects.filter(
            source_node=source_node,
            target_node=target_node,
            source_text=source_node.text,
            target_text=target_node.text,
        ).first()
        if diff:
            diff.hits += 1
            diff.save()
            diff_q = ipho_exam.qml.QMLquestion(diff.diff_text)
        else:
            diff = CachedHTMLDiff(
                source_node=source_node,
                target_node=target_node,
                source_text=source_node.text,
                target_text=target_node.text,
            )
            start = time.time()
            target_q = ipho_exam.qml.make_qml(target_node)
            target_data = target_q.flat_content_dict()
            diff_q.diff_content(target_data)
            timing = time.time() - start
            diff.diff_text = diff_q.dump()
            diff.timing = int(timing * 1000)
            diff.save()
        return diff_q


VALID_RAW_FIGURE_EXTENSIONS = (".png", ".jpg", ".jpeg")
VALID_COMPILED_FIGURE_EXTENSIONS = (".svg", ".svgz")
VALID_FIGURE_EXTENSIONS = VALID_RAW_FIGURE_EXTENSIONS + VALID_COMPILED_FIGURE_EXTENSIONS


class FigureManager(PolymorphicManager):
    def get_by_natural_key(self, fig_id):
        return self.get(fig_id=fig_id)


class Figure(PolymorphicModel):
    objects = FigureManager()
    name = models.CharField(max_length=100, db_index=True)
    fig_id = models.CharField(
        max_length=100,
        db_index=True,
        default=natural_id.generate_id,
        unique=True,
        blank=False,
    )

    def natural_key(self):
        return (self.fig_id,)

    def __str__(self):
        return "%s" % (self.name)


class CompiledFigure(Figure):
    content = models.TextField(blank=True)
    params = models.TextField(blank=True)

    def params_as_list(self):
        return list(si.trim() for si in self.params.split(","))

    def _to_svg(self, query, lang=None):
        placeholders = self.params.split(",")
        fig_svg = self.content
        fonts_repl = f"@import url({SITE_URL}/static/noto/notosans.css);"
        font_name = "Noto Sans"
        # text_direction = "ltr"
        if lang is not None:
            font_name = fonts.ipho[lang.font]["font"]
            # text_direction = lang.direction
            fonts_repl += "\n@import url({host}/static/noto/{font_css});".format(
                host=SITE_URL, font_css=fonts.ipho[lang.font]["css"]
            )
        fig_svg = fig_svg.replace("%font-faces%", fonts_repl)
        fig_svg = fig_svg.replace("%font-family%", font_name)
        # fig_svg = fig_svg.replace('%text-direction%', text_direction)
        fig_svg = fig_svg.replace("%text-direction%", "")
        for plh in placeholders:
            if plh in query:
                repl = query[plh]
                fig_svg = fig_svg.replace(f"%{plh}%", repl)
        return fig_svg

    def to_inline(self, query, lang=None):
        return self._to_svg(query=query, lang=lang), "svg+xml"

    def to_file(self, fig_name, query, lang=None, svg_to_png=False):
        fig_svg = self._to_svg(query=query, lang=lang)
        if svg_to_png:
            return self._to_png(fig_svg, fig_name)
        return self._to_pdf(fig_svg, fig_name)

    @staticmethod
    def _to_pdf(fig_svg, fig_name):
        # pylint: disable=consider-using-with
        with codecs.open("%s.svg" % (fig_name), "w", encoding="utf-8") as f:
            f.write(fig_svg)
        error = subprocess.Popen(
            [
                INKSCAPE_BIN,
                "--without-gui",
                "%s.svg" % (fig_name),
                "--export-pdf=%s.pdf" % (fig_name),
            ],
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        ).wait()
        if error:
            print("Got error", error)
            raise RuntimeError(f"Error in Inkscape. Errorcode {error}.")

    @staticmethod
    def _to_png(fig_svg, fig_name):
        # pylint: disable=consider-using-with
        with codecs.open("%s.svg" % (fig_name), "w", encoding="utf-8") as f:
            f.write(fig_svg)
        error = subprocess.Popen(
            [
                INKSCAPE_BIN,
                "--without-gui",
                "%s.svg" % (fig_name),
                "--export-png=%s.png" % (fig_name),
                "--export-dpi=180",
            ],
            stdin=open(os.devnull, encoding="utf-8"),
            stderr=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
        ).wait()
        if error:
            print("Got error", error)
            raise RuntimeError(f"Error in Inkscape. Errorcode {error}.")


class RawFigure(Figure):
    content = models.BinaryField()
    filetype = models.CharField(max_length=4)
    params = ""

    def params_as_list(self):
        return []

    def to_inline(self, *args, **kwargs):
        return self.content, self.filetype

    def to_file(
        self,
        fig_name,
        query,
        lang=None,
        format_default="auto",
        force_default=False,
        svg_to_png=False,
    ):  # pylint: disable=unused-argument, too-many-arguments
        with open(f"{fig_name}.{self.filetype}", "wb") as f:
            f.write(self.content)


class PlaceManager(models.Manager):
    def get_by_natural_key(self, name, participant_key):
        return self.get(
            name=name,
            participant=Participant.objects.get_by_natural_key(*participant_key),
        )


class Place(models.Model):
    objects = PlaceManager()

    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} [{self.participant.exam.name} {self.participant.code}]"

    def natural_key(self):
        return (self.name, self.participant.natural_key())

    class Meta:
        unique_together = index_together = ("participant",)


class Feedback(models.Model):
    STATUS_CHOICES = (
        ("S", "Submitted"),
        ("V", "Scheduled for voting"),
        ("I", "Implemented"),
        ("T", "Settled after voting"),
        ("W", "Withdrawn"),
    )
    CATEGORY_CHOICES = (
        ("T", "Typo"),
        ("F", "Formulation"),
        ("C", "Science"),
        ("S", "Structure"),
        ("O", "Other"),
    )

    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    qml_id = models.CharField(max_length=100, default=None, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    part = models.CharField(max_length=100, default=None)
    part_position = models.IntegerField(default=0)
    comment = models.TextField(blank=True)
    org_comment = models.TextField(blank=True, null=True, default=None)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="S")
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"#{self.pk} {self.question.name} - {self.question.exam.name} ({self.delegation.name})"


class FeedbackComment(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["timestamp"]


class Like(models.Model):
    CHOICES = (
        ("L", "Liked"),
        ("U", "Unliked"),
    )
    status = models.CharField(max_length=1, choices=CHOICES)
    delegation = models.ForeignKey(Delegation, on_delete=models.CASCADE)
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)

    class Meta:
        unique_together = index_together = ("delegation", "feedback")


class ExamActionManager(models.Manager):
    def get_by_natural_key(self, exam_name, delegation_name, action):
        return self.get(
            exam__name=exam_name, delegation__name=delegation_name, action=action
        )


class ExamAction(models.Model):
    objects = ExamActionManager()

    OPEN = "O"
    SUBMITTED = "S"
    STATUS_CHOICES = (
        (OPEN, "In progress"),
        (SUBMITTED, "Submitted"),
    )
    TRANSLATION = "T"
    POINTS = "P"
    ACTION_CHOICES = (
        (TRANSLATION, "Translation submission"),
        (POINTS, "Points submission"),
    )
    exam = models.ForeignKey(
        Exam, related_name="delegation_status", on_delete=models.CASCADE
    )
    delegation = models.ForeignKey(
        Delegation, related_name="exam_status", on_delete=models.CASCADE
    )
    action = models.CharField(max_length=2, choices=ACTION_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="O")
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = index_together = (("exam", "delegation", "action"),)

    def natural_key(self):
        return self.exam.natural_key() + self.delegation.natural_key() + (self.action,)

    natural_key.dependencies = ["ipho_exam.exam", "ipho_core.delegation"]

    @staticmethod
    def action_in_progress(action, exam, delegation):
        translation_submitted = ExamAction.objects.filter(
            exam=exam, delegation=delegation, action=action, status=ExamAction.SUBMITTED
        ).exists()
        return not translation_submitted

    @staticmethod
    def require_in_progress(action, exam, delegation):
        if not ExamAction.action_in_progress(action, exam, delegation):
            return IphoExamForbidden(
                "You cannot perfom this action: this exam is submitted. Contact the staff if you have good reasons to request a reset."
            )
        return None


@receiver(post_save, sender=Exam, dispatch_uid="create_actions_on_exam_creation")
def create_actions_on_exam_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for delegation in Delegation.objects.all():
        for action, _ in ExamAction.ACTION_CHOICES:
            ExamAction.objects.get_or_create(
                exam=instance, delegation=delegation, action=action
            )


@receiver(
    post_save, sender=Delegation, dispatch_uid="create_actions_on_delegation_creation"
)
def create_actions_on_delegation_creation(instance, created, raw, **kwargs):
    # Ignore fixtures and saves for existing courses.
    if not created or raw:
        return
    for exam in Exam.objects.all():
        for action, _ in ExamAction.ACTION_CHOICES:
            ExamAction.objects.get_or_create(
                exam=exam, delegation=instance, action=action
            )


class ParticipantSubmission(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    with_question = models.BooleanField(
        default=True, help_text="Deliver question sheets."
    )
    with_answer = models.BooleanField(
        default=False, help_text="Deliver also answer sheet."
    )

    ## TODO: do we need a status? (in progress, submitted, printed)

    class Meta:
        unique_together = index_together = (("participant", "language"),)


def exam_prints_filename(obj, fname):  # pylint: disable=unused-argument
    path = f"exams-docs/{obj.participant.code}/print/exam-{obj.participant.exam.id}-{obj.position}.pdf"
    return path


def exam_scans_filename(obj, fname):  # pylint: disable=unused-argument
    path = f"exams-docs/{obj.participant.code}/scan/exam-{obj.participant.exam.id}-{obj.position}.pdf"
    return path


def exam_scans_orig_filename(obj, fname):  # pylint: disable=unused-argument
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    path = f"scans-evaluated/{obj.barcode_base}__{timestamp}.pdf"
    return path


class DocumentManager(models.Manager):
    def for_user(self, user):
        queryset = self.get_queryset()
        if (
            user.is_superuser
            or user.has_perm("ipho_core.is_organizer_admin")
            or user.has_perm("ipho_core.is_marker")
        ):
            return queryset.filter(participant__exam__in=Exam.objects.for_user(user))
        if user.has_perm("ipho_core.is_printstaff"):
            # Does show documents even if printing is not activated as there is no scanning flag for organizers at the moment.
            return queryset.filter(participant__exam__in=Exam.objects.for_user(user))
        if user.has_perm("ipho_core.is_delegation"):
            delegs = Delegation.objects.filter(members=user)
            return queryset.filter(
                participant__exam__in=Exam.objects.for_user(user)
            ).filter(participant__delegation__in=delegs)
        return queryset.none()

    def scans_ready(self, user):
        queryset = self.for_user(user)
        return (
            queryset.filter(scan_status="S")
            .exclude(
                scan_file__isnull=True,
            )
            .exclude(scan_file="")
        )


class Document(models.Model):
    objects = DocumentManager()

    SCAN_STATUS_CHOICES = (
        ("S", "Success"),
        ("W", "Warning"),
        ("M", "Missing pages"),
    )

    participant = models.ForeignKey(
        Participant, help_text="Participant", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now=True, null=True)
    position = models.IntegerField(
        help_text="Question grouping position, e.g. 0 for cover sheet / instructions, 1 for the first question, etc"
    )
    file = models.FileField(
        blank=True, upload_to=exam_prints_filename, help_text="Exam handouts"
    )
    num_pages = models.IntegerField(
        default=0, help_text="Number of pages of the handouts"
    )
    barcode_num_pages = models.IntegerField(
        default=0, help_text="Number of pages with a barcode"
    )
    extra_num_pages = models.IntegerField(
        default=0,
        help_text="Number of additional pages with barcode (not in the handouts)",
    )
    barcode_base = models.TextField(help_text="Common base barcode on all pages")
    scan_file = models.FileField(
        blank=True,
        upload_to=exam_scans_filename,
        help_text="Scanned results. The file is show to the delegation and, if possible, it will contain only the pages with barcode.",
    )
    scan_file_orig = models.FileField(
        blank=True,
        upload_to=exam_scans_orig_filename,
        help_text="Original scanned document without page extractions",
    )
    scan_status = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=SCAN_STATUS_CHOICES,
        help_text="Status of the scanned document. S - Success, W - Warning, M - Missing pages",
    )
    scan_msg = models.TextField(
        blank=True,
        null=True,
        help_text="Warning messages generated by the barcode extractor",
    )

    class Meta:
        unique_together = index_together = (("participant", "position"),)
        ordering = ["participant", "position"]

    # def question_name(self):
    # return self.question.name

    def __str__(self):
        return f"Document: {self.participant.exam.name} #{self.position} [{self.participant.code}]"


class DocumentTask(models.Model):
    task_id = models.CharField(unique=True, max_length=255)
    document = models.OneToOneField(Document, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.task_id} --> {self.document}"


class PrintLog(models.Model):
    TYPE_CHOICES = (("P", "Printout"), ("S", "Scan"))
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    doctype = models.CharField(max_length=1, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document.participant.exam.code}-{self.document.position} ({self.doctype}) {self.timestamp}"
