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
        "pdf/solution/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question,
        {"solution": True},
        name="pdf-solution",
    ),
    path(
        "pdf/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        name="pdf-version",
    ),
    path(
        "pdf/solution/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        {"solution": True},
        name="pdf-solution-version",
    ),
    path(
        "pdf-diff/question/<int:question_id>/lang/<int:lang_id>/v<int:old_version_num>/v<int:new_version_num>",
        views.compiled_question_diff,
        name="pdfdiff-version",
    ),
    path(
        "pdf-diff/solution/<int:question_id>/lang/<int:lang_id>/v<int:old_version_num>/v<int:new_version_num>",
        views.compiled_question_diff,
        {"solution": True},
        name="pdfdiff-solution-version",
    ),
    path(
        "tex/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question,
        {"raw_tex": True},
        name="tex",
    ),
    path(
        "tex/solution/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question,
        {"raw_tex": True, "solution": True},
        name="tex-solution",
    ),
    path(
        "tex/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        {"raw_tex": True},
        name="tex-version",
    ),
    path(
        "tex/solution/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question,
        {"raw_tex": True, "solution": True},
        name="tex-solution-version",
    ),
    path(
        "odt/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_odt,
        name="odt",
    ),
    path(
        "odt/solution/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_odt,
        {"solution": True},
        name="odt-solution",
    ),
    path(
        "odt/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_odt,
        name="odt-version",
    ),
    path(
        "odt/solution/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_odt,
        {"solution": True},
        name="odt-solution-version",
    ),
    path(
        "html/question/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_html,
        name="html",
    ),
    path(
        "html/solution/<int:question_id>/lang/<int:lang_id>",
        views.compiled_question_html,
        {"solution": True},
        name="html-solution",
    ),
    path(
        "html/question/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_html,
        name="html-version",
    ),
    path(
        "html/solution/<int:question_id>/lang/<int:lang_id>/v<int:version_num>",
        views.compiled_question_html,
        {"solution": True},
        name="html-solution-version",
    ),
    path(
        "pdf/exam/<int:exam_id>/<int:position>/participant/<int:participant_id>",
        views.pdf_exam_pos_participant,
        {"type": "P"},
        name="pdf-exam-pos-participant",
    ),
    path(
        "pdf/exam/<int:exam_id>/<int:position>/participant/<int:participant_id>/status",
        views.pdf_exam_pos_participant_status,
        name="pdf-exam-pos-participant-status",
    ),
    path(
        "scan/exam/<int:exam_id>/<int:position>/participant/<int:participant_id>",
        views.pdf_exam_pos_participant,
        {"type": "S"},
        name="scan-exam-pos-participant",
    ),
    path(
        "scan_orig/exam/<int:exam_id>/<int:position>/participant/<int:participant_id>",
        views.pdf_exam_pos_participant,
        {"type": "O"},
        name="scan-orig-exam-pos-participant",
    ),
    re_path(
        r"^print/(?P<doctype>\w)/(?P<exam_id>\d+)/(?P<position>\d+)/participant/(?P<participant_id>\d+)/queue/(?P<queue>.+)$",
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
        r"^feedbacks/thread/?$",
        views.feedback_thread,
        name="feedback-thread",
    ),
    re_path(
        r"^feedbacks/(?P<feedback_id>\d+)/status/(?P<status>\w)$",
        views.feedback_set_status,
        name="feedback-set-status",
    ),
    re_path(
        r"^feedbacks/(?P<feedback_id>\d+)/category/(?P<category>\w)$",
        views.feedback_set_category,
        name="feedback-set-category",
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
        "submission/submitted/scan/exam/<int:exam_id>/<int:position>/participant/<int:participant_id>",
        views.upload_scan_delegation,
        name="submission-delegation-submitted-scan-upload",
    ),
    path(
        "submission/submitted/scan/exam/many",
        views.upload_many_scan_delegation,
        name="submission-delegation-submitted-scan-many",
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
    path(
        "admin/",
        views.admin,
        name="admin",
    ),
    path(
        "admin/<int:exam_id>/",
        views.admin,
        name="admin-exam",
    ),
    path(
        "admin/exam-detail/<int:exam_id>/",
        views.admin_exam_detail,
        name="admin-exam-detail",
    ),
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
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/check_before_accept",
        views.admin_check_version_before_diff,
        name="admin-check-version-before-diff",
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
        "admin/<int:exam_id>/<int:question_id>/v<int:version_num>/check_points",
        views.admin_check_points,
        name="admin-check-points",
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
    path(
        "admin/scan-progress/<int:question_id>",
        views.admin_scan_progress,
        name="admin-scan-progress",
    ),
    path(
        "admin/scan-progress",
        views.admin_scan_progress,
        name="admin-scan-progress",
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
        "admin/mark-scan-as-printed/<int:doc_id>",
        views.mark_scan_as_printed,
        name="mark-scan-as-printed",
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
