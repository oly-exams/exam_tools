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

from django.urls import include, path, re_path

from . import views

app_name = "exam"
urlpatterns = [
    path("", views.index, name="index"),
    path("wizard", views.wizard, name="wizard"),
    path("main", views.main, name="main"),
    re_path(r"^translation/list/?$", views.translations_list, name="list"),
    path(
        "translation/add/<int:exam_id>",
        views.add_translation,
        name="add-translation",
    ),
    path(
        "translation/upload/question/<int:question_id>/lang/<int:lang_id>",
        views.add_pdf_node,
        name="upload-translation",
    ),
    path(
        "translation/export/question/<int:question_id>/lang/<int:lang_id>",
        views.translation_export,
        name="export-translation",
    ),
    path(
        "translation/export/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.translation_export,
        name="export-translation-version",
    ),
    path(
        "translation/import/question/<int:question_id>/lang/<int:lang_id>",
        views.translation_import,
        name="import-translation",
    ),
    re_path(
        r"^translation/import/confirm/(?P<slug>[0-9a-z\-]+)$",
        views.translation_import_confirm,
        name="import-translation-confirm",
    ),
    re_path(r"^translation/all/?$", views.list_all_translations, name="list-all"),
    path("auto-translate", views.auto_translate, name="auto-translate"),
    path(
        "auto-translate-count",
        views.auto_translate_count,
        name="auto-translate-count",
    ),
    re_path(r"^languages/?$", views.list_language, name="language-list"),
    path("languages/add", views.add_language, name="language-add"),
    path("languages/edit/<int:lang_id>", views.edit_language, name="language-edit"),
    path("time", views.time_response, name="time"),
    re_path(r"^editor/?$", views.editor),
    path("editor/<int:exam_id>", views.editor, name="editor-exam"),
    path(
        "editor/<int:exam_id>/question/<int:question_id>",
        views.editor,
        name="editor-question",
    ),
    path(
        "editor/<int:exam_id>/question/<int:question_id>/orig/<int:orig_id>",
        views.editor,
        name="editor-orig",
    ),
    path(
        "editor/<int:exam_id>/question/<int:question_id>/orig/<int:orig_id>/lang/<int:lang_id>",
        views.editor,
        name="editor-orig-lang",
    ),
    path(
        "editor/<int:exam_id>/question/<int:question_id>/orig_diff/<int:orig_id>v<int:orig_diff>",
        views.editor,
        name="editor-origdiff",
    ),
    path(
        "editor/<int:exam_id>/question/<int:question_id>/orig_diff/<int:orig_id>v<int:orig_diff>/lang/<int:lang_id>",
        views.editor,
        name="editor-origdiff-lang",
    ),
    path("view", views.exam_view, name="exam-view"),
    path("view/<int:exam_id>", views.exam_view, name="exam-view"),
    path(
        "view/<int:exam_id>/question/<int:question_id>",
        views.exam_view,
        name="exam-view",
    ),
    path(
        "pdf/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question,
        name="pdf",
    ),
    path(
        "pdf/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        name="pdf-version",
    ),
    path(
        "pdf-diff/question/<int:question_id>/lang/<int:lang_id>/v<int:old_version_num>/v<int:new_version_num>",
        views.compiled_question_diff,
        name="pdfdiff-version",
    ),
    path(
        "tex/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question,
        {"raw_tex": True},
        name="tex",
    ),
    path(
        "tex/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        {"raw_tex": True},
        name="tex-version",
    ),
    path(
        "odt/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_odt,
        name="odt",
    ),
    path(
        "odt/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_odt,
        name="odt-version",
    ),
    path(
        "html/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_html,
        name="html",
    ),
    path(
        "html/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_html,
        name="html-version",
    ),
    path(
        "pdf/exam/<int:exam_id>/student/<int:student_id>",
        views.pdf_exam_for_student,
        name="pdf-exam-student",
    ),
    path(
        "pdf/exam/<int:exam_id>/<int:position>/student/<int:student_id>",
        views.pdf_exam_pos_student,
        {"type": "P"},
        name="pdf-exam-pos-student",
    ),
    path(
        "pdf/exam/<int:exam_id>/<int:position>/student/<int:student_id>/status",
        views.pdf_exam_pos_student_status,
        name="pdf-exam-pos-student-status",
    ),
    path(
        "scan/exam/<int:exam_id>/<int:position>/student/<int:student_id>",
        views.pdf_exam_pos_student,
        {"type": "S"},
        name="scan-exam-pos-student",
    ),
    path(
        "scan_orig/exam/<int:exam_id>/<int:position>/student/<int:student_id>",
        views.pdf_exam_pos_student,
        {"type": "O"},
        name="scan-orig-exam-pos-student",
    ),
    re_path(
        r"^print/(?P<doctype>\w)/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)/queue/(?P<queue>.+)$",
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
    path("feedbacks/add", views.feedbacks_add_comment, name="feedback-add-comment"),
    path(
        "feedbacks/add/<int:feedback_id>",
        views.feedbacks_add_comment,
        name="feedback-add-comment",
    ),
    path(
        "feedbacks/numbers/<int:exam_id>/<int:question_id>",
        views.feedback_numbers,
        name="feedback-numbers",
    ),
    path(
        "feedbacks/partial/<int:exam_id>/<int:question_id>",
        views.feedback_partial,
        name="feedback-partial",
    ),
    re_path(
        r"^feedbacks/partial/(?P<exam_id>\d+)/(?P<question_id>\d+)/(?P<qml_id>[0-9a-z\-\_]+)$",
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
    path("submission/list", views.submission_exam_list, name="submission-exam-list"),
    path(
        "submission/<int:exam_id>/assign",
        views.submission_exam_assign,
        name="submission-exam-assign",
    ),
    path(
        "submission/<int:exam_id>/confirm",
        views.submission_exam_confirm,
        name="submission-exam-confirm",
    ),
    path(
        "submission/<int:exam_id>/submitted",
        views.submission_exam_submitted,
        name="submission-exam-submitted",
    ),
    re_path(
        r"^submission/submitted/?$",
        views.submission_delegation_list_submitted,
        name="submission-delegation-submitted",
    ),
    path(
        "submission/submitted/scan/exam/<int:exam_id>/<int:position>/student/<int:student_id>",
        views.upload_scan_delegation,
        name="submission-delegation-submitted-scan-upload",
    ),
    re_path(r"^figures/?$", views.figure_list, name="figures"),
    path("figure/add", views.figure_add, name="figure-add"),
    path("figure/<str:fig_id>", views.figure_edit, name="figure-edit"),
    path("figure/<str:fig_id>/remove", views.figure_delete, name="figure-delete"),
    path("figure/<str:fig_id>/export", views.figure_export, name="figure-export"),
    path(
        "figure/<str:fig_id>/<int:lang_id>/export",
        views.figure_export,
        name="figure-lang-export",
    ),
    re_path(r"^admin/?$", views.admin_list, name="admin"),
    path(
        "admin/<int:exam_id>/question/add",
        views.admin_add_question,
        name="admin-add-question",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/question/delete",
        views.admin_delete_question,
        name="admin-delete-question",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/question/edit",
        views.admin_edit_question,
        name="admin-edit-question",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/newversion",
        views.admin_new_version,
        name="admin-new-version",
    ),
    path(
        "admin/<int:question_id>/import",
        views.admin_import_version,
        name="admin-import-version",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/delete",
        views.admin_delete_version,
        name="admin-delete-version",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/accept",
        views.admin_accept_version,
        name="admin-accept-version",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/publish",
        views.admin_publish_version,
        name="admin-publish-version",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/settag",
        views.admin_settag_version,
        name="admin-settag-version",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:compare_version>/v<int:version_num>/accept",
        views.admin_accept_version,
        name="admin-accept-version-diff",
    ),
    path(
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/editor",
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
    path(
        "admin/feedbacks/export",
        views.feedbacks_export,
        name="admin-feedbacks-export-main",
    ),
    path(
        "admin/feedbacks/export/E<int:exam_id>_<int:question_id>.csv",
        views.feedbacks_export_csv,
        name="admin-feedbacks-export-csv",
    ),
    path(
        "admin/submissions/translation",
        views.admin_submissions_translation,
        name="admin-submissions-translation",
    ),
    path(
        "admin/print/submissions/translation",
        views.print_submissions_translation,
        name="print-submissions-translation",
    ),
    path(
        "admin/submissions/list/<int:exam_id>",
        views.admin_submission_list,
        name="admin-submission-list",
    ),
    path(
        "admin/submissions/assign/<int:exam_id>",
        views.admin_submission_assign,
        name="admin-submission-assign",
    ),
    path(
        "admin/submissions/<int:submission_id>/delete",
        views.admin_submission_delete,
        name="admin-submission-delete",
    ),
    re_path(r"^admin/bulk-print/?$", views.bulk_print, name="bulk-print"),
    path(
        "admin/bulk-print/<int:page>/<int:tot_print>",
        views.bulk_print,
        name="bulk-print_prg",
    ),
    re_path(
        r"^admin/extra-sheets/?$", views.extra_sheets, name="extra-sheets-select-exam"
    ),
    path(
        "admin/extra-sheets/<int:exam_id>",
        views.extra_sheets,
        name="extra-sheets",
    ),
    path(
        "admin/scan-status/<int:doc_id>/<slug:status>",
        views.set_scan_status,
        name="set-scan-status",
    ),
    path(
        "admin/scan/promote-full/<int:doc_id>",
        views.set_scan_full,
        name="set-scan-full",
    ),
    path("admin/scan/upload", views.upload_scan, name="upload-scan"),
    path("admin/api_keys", views.api_keys, name="api-keys"),
    path("test/", include("ipho_exam.urls_test", namespace="test")),
    # re_path(r'^(?P<rep_id>\d+)/submit/?$', views.submit),
]
