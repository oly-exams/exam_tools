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

from django.conf.urls import include, re_path

from . import views

app_name = "exam"
urlpatterns = [
    re_path(r"^$", views.index, name="index"),
    re_path(r"^wizard$", views.wizard, name="wizard"),
    re_path(r"^main$", views.main, name="main"),
    re_path(r"^translation/list/?$", views.translations_list, name="list"),
    re_path(
        r"^translation/add/(?P<exam_id>\d+)$",
        views.add_translation,
        name="add-translation",
    ),
    re_path(
        r"^translation/upload/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$",
        views.add_pdf_node,
        name="upload-translation",
    ),
    re_path(
        r"^translation/export/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$",
        views.translation_export,
        name="export-translation",
    ),
    re_path(
        r"^translation/export/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)",
        views.translation_export,
        name="export-translation-version",
    ),
    re_path(
        r"^translation/import/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$",
        views.translation_import,
        name="import-translation",
    ),
    re_path(
        r"^translation/import/confirm/(?P<slug>[0-9a-z\-]+)$",
        views.translation_import_confirm,
        name="import-translation-confirm",
    ),
    re_path(r"^translation/all/?$", views.list_all_translations, name="list-all"),
    re_path(r"^auto-translate$", views.auto_translate, name="auto-translate"),
    re_path(
        r"^auto-translate-count$",
        views.auto_translate_count,
        name="auto-translate-count",
    ),
    re_path(r"^languages/?$", views.list_language, name="language-list"),
    re_path(r"^languages/add$", views.add_language, name="language-add"),
    re_path(
        r"^languages/edit/(?P<lang_id>\d+)$", views.edit_language, name="language-edit"
    ),
    re_path(r"^time$", views.time_response, name="time"),
    re_path(r"^editor/?$", views.editor),
    re_path(r"^editor/(?P<exam_id>\d+)$", views.editor, name="editor-exam"),
    re_path(
        r"^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$",
        views.editor,
        name="editor-question",
    ),
    re_path(
        r"^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)$",
        views.editor,
        name="editor-orig",
    ),
    re_path(
        r"^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)/lang/(?P<lang_id>\d+)?$",
        views.editor,
        name="editor-orig-lang",
    ),
    re_path(
        r"^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)$",
        views.editor,
        name="editor-origdiff",
    ),
    re_path(
        r"^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)/lang/(?P<lang_id>\d+)?$",
        views.editor,
        name="editor-origdiff-lang",
    ),
    re_path(r"^view$", views.exam_view, name="exam-view"),
    re_path(r"^view/(?P<exam_id>\d+)$", views.exam_view, name="exam-view"),
    re_path(
        r"^view/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$",
        views.exam_view,
        name="exam-view",
    ),
    re_path(
        r"^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$",
        views.compiled_question,
        name="pdf",
    ),
    re_path(
        r"^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$",
        views.compiled_question,
        name="pdf-version",
    ),
    re_path(
        r"^pdf-diff/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<old_version_num>\d+)/v(?P<new_version_num>\d+)$",
        views.compiled_question_diff,
        name="pdfdiff-version",
    ),
    re_path(
        r"^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$",
        views.compiled_question,
        {"raw_tex": True},
        name="tex",
    ),
    re_path(
        r"^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$",
        views.compiled_question,
        {"raw_tex": True},
        name="tex-version",
    ),
    re_path(
        r"^odt/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$",
        views.compiled_question_odt,
        name="odt",
    ),
    re_path(
        r"^odt/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$",
        views.compiled_question_odt,
        name="odt-version",
    ),
    re_path(
        r"^html/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$",
        views.compiled_question_html,
        name="html",
    ),
    re_path(
        r"^html/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$",
        views.compiled_question_html,
        name="html-version",
    ),
    re_path(
        r"^pdf/exam/(?P<exam_id>\d+)/student/(?P<student_id>\d+)$",
        views.pdf_exam_for_student,
        name="pdf-exam-student",
    ),
    re_path(
        r"^pdf/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$",
        views.pdf_exam_pos_student,
        {"type": "P"},
        name="pdf-exam-pos-student",
    ),
    re_path(
        r"^pdf/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)/status$",
        views.pdf_exam_pos_student_status,
        name="pdf-exam-pos-student-status",
    ),
    re_path(
        r"^scan/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$",
        views.pdf_exam_pos_student,
        {"type": "S"},
        name="scan-exam-pos-student",
    ),
    re_path(
        r"^scan_orig/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$",
        views.pdf_exam_pos_student,
        {"type": "O"},
        name="scan-orig-exam-pos-student",
    ),
    re_path(
        r"^print/(?P<type>\w)/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)/queue/(?P<queue>.+)$",
        views.print_doc,
        name="print-doc",
    ),
    re_path(r"^pdf-task/(?P<token>[0-9a-z\-]+)$", views.pdf_task, name="pdf-task"),
    re_path(
        r"^pdf-task/(?P<token>[0-9a-z\-]+)/status$",
        views.task_status,
        name="pdf-task-status",
    ),
    re_path(
        r"^pdf-task/(?P<token>[0-9a-z\-]+)/log$", views.task_log, name="pdf-task-log"
    ),
    re_path(r"^feedbacks/list/?$", views.feedbacks_list, name="feedbacks-list"),
    re_path(
        r"^feedbacks/list/(?P<exam_id>\d+)/?$",
        views.feedbacks_list,
        name="feedbacks-list",
    ),
    re_path(
        r"^feedbacks/add$", views.feedbacks_add_comment, name="feedback-add-comment"
    ),
    re_path(
        r"^feedbacks/add/(?P<feedback_id>\d+)$",
        views.feedbacks_add_comment,
        name="feedback-add-comment",
    ),
    re_path(
        r"^feedbacks/numbers/(?P<exam_id>\d+)/(?P<question_id>\d+)$",
        views.feedback_numbers,
        name="feedback-numbers",
    ),
    re_path(
        r"^feedbacks/partial/(?P<exam_id>\d+)/(?P<question_id>\d+)$",
        views.feedback_partial,
        name="feedback-partial",
    ),
    re_path(
        r"^feedbacks/partial/(?P<exam_id>\d+)/(?P<question_id>\d+)/(?P<qml_id>[0-9a-z\-]+)$",
        views.feedback_partial,
        name="feedback-partial",
    ),
    re_path(
        r"^feedbacks/(?P<status>(U|L))/(?P<feedback_id>\d+)$",
        views.feedback_partial_like,
        name="feedback-like",
    ),
    re_path(
        r"^feedbacks/(?P<feedback_id>\d+)/status/(?P<status>\w)$",
        views.feedback_set_status,
        name="feedback-set-status",
    ),
    re_path(
        r"^submission/list$", views.submission_exam_list, name="submission-exam-list"
    ),
    re_path(
        r"^submission/(?P<exam_id>\d+)/assign$",
        views.submission_exam_assign,
        name="submission-exam-assign",
    ),
    re_path(
        r"^submission/(?P<exam_id>\d+)/confirm$",
        views.submission_exam_confirm,
        name="submission-exam-confirm",
    ),
    re_path(
        r"^submission/(?P<exam_id>\d+)/submitted$",
        views.submission_exam_submitted,
        name="submission-exam-submitted",
    ),
    re_path(
        r"^submission/submitted/?$",
        views.submission_delegation_list_submitted,
        name="submission-delegation-submitted",
    ),
    re_path(
        r"^submission/submitted/scan/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)?$",
        views.upload_scan_delegation,
        name="submission-delegation-submitted-scan-upload",
    ),
    re_path(r"^figures/?$", views.figure_list, name="figures"),
    re_path(r"^figure/add$", views.figure_add, name="figure-add"),
    re_path(r"^figure/(?P<fig_id>[^\/]+)$", views.figure_edit, name="figure-edit"),
    re_path(
        r"^figure/(?P<fig_id>[^\/]+)/remove$", views.figure_delete, name="figure-delete"
    ),
    re_path(
        r"^figure/(?P<fig_id>[^\/]+)/export$", views.figure_export, name="figure-export"
    ),
    re_path(
        r"^figure/(?P<fig_id>[^\/]+)/(?P<lang_id>\d+)/export$",
        views.figure_export,
        name="figure-lang-export",
    ),
    re_path(r"^admin/?$", views.admin_list, name="admin"),
    re_path(
        r"^admin/(?P<exam_id>\d+)/quesiton/add$",
        views.admin_add_question,
        name="admin-add-question",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/question/delete$",
        views.admin_delete_question,
        name="admin-delete-question",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/question/edit$",
        views.admin_edit_question,
        name="admin-edit-question",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/newversion$",
        views.admin_new_version,
        name="admin-new-version",
    ),
    re_path(
        r"^admin/(?P<question_id>\d+)/import$",
        views.admin_import_version,
        name="admin-import-version",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/delete$",
        views.admin_delete_version,
        name="admin-delete-version",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/accept$",
        views.admin_accept_version,
        name="admin-accept-version",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/publish$",
        views.admin_publish_version,
        name="admin-publish-version",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/settag$",
        views.admin_settag_version,
        name="admin-settag-version",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<compare_version>\d+)/v(?P<version_num>\d+)/accept$",
        views.admin_accept_version,
        name="admin-accept-version-diff",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor$",
        views.admin_editor,
        name="admin-editor",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/edit/(?P<block_id>\w+)$",
        views.admin_editor_block,
        name="admin-editor-block",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/delete/(?P<block_id>\w+)$",
        views.admin_editor_delete_block,
        name="admin-editor-delete-block",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/add/(?P<block_id>\w+)/(?P<tag_name>\w+)$",
        views.admin_editor_add_block,
        name="admin-editor-add-block",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/add/(?P<block_id>\w+)/(?P<after_id>\w+)/(?P<tag_name>\w+)$",
        views.admin_editor_add_block,
        name="admin-editor-add-block-after",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/moveup/(?P<parent_id>\w+)/(?P<block_id>\w+)$",
        views.admin_editor_move_block,
        {"direction": "up"},
        name="admin-editor-moveup-block",
    ),
    re_path(
        r"^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/movedown/(?P<parent_id>\w+)/(?P<block_id>\w+)$",
        views.admin_editor_move_block,
        {"direction": "down"},
        name="admin-editor-movedown-block",
    ),
    re_path(
        r"^admin/feedbacks/export$",
        views.feedbacks_export,
        name="admin-feedbacks-export-main",
    ),
    re_path(
        r"^admin/feedbacks/export/E(?P<exam_id>\d+)_(?P<question_id>\d+).csv$",
        views.feedbacks_export_csv,
        name="admin-feedbacks-export-csv",
    ),
    re_path(
        r"^admin/submissions/translation$",
        views.admin_submissions_translation,
        name="admin-submissions-translation",
    ),
    re_path(
        r"^admin/print/submissions/translation$",
        views.print_submissions_translation,
        name="print-submissions-translation",
    ),
    re_path(
        r"^admin/submissions/list/(?P<exam_id>\d+)$",
        views.admin_submission_list,
        name="admin-submission-list",
    ),
    re_path(
        r"^admin/submissions/assign/(?P<exam_id>\d+)$",
        views.admin_submission_assign,
        name="admin-submission-assign",
    ),
    re_path(
        r"^admin/submissions/(?P<submission_id>\d+)/delete$",
        views.admin_submission_delete,
        name="admin-submission-delete",
    ),
    re_path(r"^admin/bulk-print/?$", views.bulk_print, name="bulk-print"),
    re_path(
        r"^admin/bulk-print/(?P<page>\d+)/(?P<tot_print>\d+)$",
        views.bulk_print,
        name="bulk-print_prg",
    ),
    re_path(
        r"^admin/extra-sheets/?$", views.extra_sheets, name="extra-sheets-select-exam"
    ),
    re_path(
        r"^admin/extra-sheets/(?P<exam_id>\d+)$",
        views.extra_sheets,
        name="extra-sheets",
    ),
    re_path(
        r"^admin/scan-status/(?P<doc_id>\d+)/(?P<status>\w)$",
        views.set_scan_status,
        name="set-scan-status",
    ),
    re_path(
        r"^admin/scan/promote-full/(?P<doc_id>\d+)$",
        views.set_scan_full,
        name="set-scan-full",
    ),
    re_path(r"^admin/scan/upload$", views.upload_scan, name="upload-scan"),
    re_path(r"^admin/api_keys$", views.api_keys, name="api-keys"),
    re_path(r"^test/", include("ipho_exam.urls_test", namespace="test")),
    # re_path(r'^(?P<rep_id>\d+)/submit/?$', views.submit),
]
