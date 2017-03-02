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

from django.conf.urls import patterns, include, url


urlpatterns = patterns('ipho_exam.views',

    url(r'^/?$', 'index', name='index'),
    url(r'^wizard$', 'wizard', name='wizard'),
    url(r'^main$', 'main', name='main'),

    url(r'^translation/list/?$', 'translations_list', name='list'),
    url(r'^translation/add/(?P<exam_id>\d+)$', 'add_translation', name='add-translation'),
    url(r'^translation/upload/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$', 'add_pdf_node', name='upload-translation'),
    url(r'^translation/export/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$', 'translation_export', name='export-translation'),
    url(r'^translation/export/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)', 'translation_export', name='export-translation-version'),
    url(r'^translation/import/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$', 'translation_import', name='import-translation'),
    url(r'^translation/import/confirm/(?P<slug>[0-9a-z\-]+)$', 'translation_import_confirm', name='import-translation-confirm'),
    url(r'^translation/all/?$', 'list_all_translations', name='list-all'),

    url(r'^languages/?$', 'list_language', name='language-list'),
    url(r'^languages/add$', 'add_language', name='language-add'),
    url(r'^languages/edit/(?P<lang_id>\d+)$', 'edit_language', name='language-edit'),

    url(r'^time$', 'time_response', name='time'),

    url(r'^editor/?$', 'editor'),
    url(r'^editor/(?P<exam_id>\d+)$', 'editor', name='editor-exam'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$', 'editor', name='editor-question'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)$', 'editor', name='editor-orig'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)/lang/(?P<lang_id>\d+)?$', 'editor', name='editor-orig-lang'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)$', 'editor', name='editor-origdiff'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)/lang/(?P<lang_id>\d+)?$', 'editor', name='editor-origdiff-lang'),

    url(r'^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'compiled_question', name='pdf'),
    url(r'^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$', 'compiled_question', name='pdf-version'),
    url(r'^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'compiled_question', {'raw_tex': True}, name='tex'),
    url(r'^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$', 'compiled_question', {'raw_tex': True}, name='tex-version'),
    url(r'^odt/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'compiled_question_odt', name='odt'),
    url(r'^html/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$', 'compiled_question_html', name='html'),
    url(r'^html/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/v(?P<version_num>\d+)$', 'compiled_question_html', name='html-version'),
    url(r'^pdf/exam/(?P<exam_id>\d+)/student/(?P<student_id>\d+)$', 'pdf_exam_for_student', name='pdf-exam-student'),
    url(r'^pdf/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$', 'pdf_exam_pos_student',  {'type': 'P'}, name='pdf-exam-pos-student'),
    url(r'^pdf/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)/status$', 'pdf_exam_pos_student_status', name='pdf-exam-pos-student-status'),
    url(r'^scan/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$', 'pdf_exam_pos_student', {'type': 'S'}, name='scan-exam-pos-student'),
    url(r'^scan_orig/exam/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)$', 'pdf_exam_pos_student', {'type': 'O'}, name='scan-orig-exam-pos-student'),
    url(r'^print/(?P<type>\w)/(?P<exam_id>\d+)/(?P<position>\d+)/student/(?P<student_id>\d+)/queue/(?P<queue>.+)$', 'print_doc', name='print-doc'),

    url(r'^pdf-task/(?P<token>[0-9a-z\-]+)$', 'pdf_task', name='pdf-task'),
    url(r'^pdf-task/(?P<token>[0-9a-z\-]+)/status$', 'task_status', name='pdf-task-status'),
    url(r'^pdf-task/(?P<token>[0-9a-z\-]+)/log$', 'task_log', name='pdf-task-log'),

    url(r'^feedbacks/list/?$', 'feedbacks_list', name='feedbacks-list'),
    url(r'^feedbacks/add/(?P<exam_id>\d+)$', 'feedbacks_add', name='feedbacks-add'),
    url(r'^feedbacks/(?P<status>(U|L))/(?P<feedback_id>\d+)$', 'feedback_like', name='feedback-like'),
    url(r'^feedbacks/(?P<feedback_id>\d+)/status/(?P<status>\w)$', 'feedback_set_status', name='feedback-set-status'),

    url(r'^submission/list$', 'submission_exam_list', name='submission-exam-list'),
    url(r'^submission/(?P<exam_id>\d+)/assign$', 'submission_exam_assign', name='submission-exam-assign'),
    url(r'^submission/(?P<exam_id>\d+)/confirm$', 'submission_exam_confirm', name='submission-exam-confirm'),
    url(r'^submission/(?P<exam_id>\d+)/submitted$', 'submission_exam_submitted', name='submission-exam-submitted'),
    url(r'^submission/(?P<exam_id>\d+)/summary$', 'submission_summary', name='submission-summary'),

    url(r'^figures/?$', 'figure_list', name='figures'),
    url(r'^figure/add$', 'figure_add', name='figure-add'),
    url(r'^figure/(?P<fig_id>\d+)$', 'figure_edit', name='figure-edit'),
    url(r'^figure/(?P<fig_id>\d+)/remove$', 'figure_delete', name='figure-delete'),
    url(r'^figure/(?P<fig_id>\d+)/export.svg$', 'figure_export', {'output_format': 'svg'}, name='figure-export'),
    url(r'^figure/(?P<fig_id>\d+)/export.pdf$', 'figure_export', {'output_format': 'pdf'}, name='figure-export-pdf'),
    url(r'^figure/(?P<fig_id>\d+)/(?P<lang_id>\d+)/export.svg$', 'figure_export', {'output_format': 'svg'}, name='figure-lang-export'),
    url(r'^figure/(?P<fig_id>\d+)/(?P<lang_id>\d+)/export.pdf$', 'figure_export', {'output_format': 'pdf'}, name='figure-lang-export-pdf'),

    url(r'^admin/?$', 'admin_list', name='admin'),
    url(r'^admin/(?P<exam_id>\d+)/quesiton/add$', 'admin_add_question', name='admin-add-question'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/newversion$', 'admin_new_version', name='admin-new-version'),
    url(r'^admin/(?P<question_id>\d+)/import$', 'admin_import_version', name='admin-import-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/delete$', 'admin_delete_version', name='admin-delete-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/accept$', 'admin_accept_version', name='admin-accept-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/publish$', 'admin_publish_version', name='admin-publish-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<compare_version>\d+)/v(?P<version_num>\d+)/accept$', 'admin_accept_version', name='admin-accept-version-diff'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor$', 'admin_editor', name='admin-editor'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/edit/(?P<block_id>\w+)$', 'admin_editor_block', name='admin-editor-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/delete/(?P<block_id>\w+)$', 'admin_editor_delete_block', name='admin-editor-delete-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/add/(?P<block_id>\w+)/(?P<tag_name>\w+)$', 'admin_editor_add_block', name='admin-editor-add-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/add/(?P<block_id>\w+)/(?P<after_id>\w+)/(?P<tag_name>\w+)$', 'admin_editor_add_block', name='admin-editor-add-block-after'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/moveup/(?P<parent_id>\w+)/(?P<block_id>\w+)$', 'admin_editor_move_block', {'direction': 'up'}, name='admin-editor-moveup-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/movedown/(?P<parent_id>\w+)/(?P<block_id>\w+)$', 'admin_editor_move_block', {'direction': 'down'}, name='admin-editor-movedown-block'),

    url(r'^admin/feedbacks/export$', 'feedbacks_export', name='admin-feedbacks-export-main'),
    url(r'^admin/feedbacks/export/E(?P<exam_id>\d+)_(?P<question_id>\d+).csv$', 'feedbacks_export_csv', name='admin-feedbacks-export-csv'),

    url(r'^admin/submissions/list/(?P<exam_id>\d+)$', 'admin_submission_list', name='admin-submission-list'),
    url(r'^admin/submissions/assign/(?P<exam_id>\d+)$', 'admin_submission_assign', name='admin-submission-assign'),
    url(r'^admin/submissions/(?P<submission_id>\d+)/delete$', 'admin_submission_delete', name='admin-submission-delete'),

    url(r'^admin/bulk-print/?$', 'bulk_print', name='bulk-print'),
    url(r'^admin/extra-sheets/?$', 'extra_sheets', name='extra-sheets-select-exam'),
    url(r'^admin/extra-sheets/(?P<exam_id>\d+)$', 'extra_sheets', name='extra-sheets'),
    url(r'^admin/scan-status/(?P<doc_id>\d+)/(?P<status>\w)$', 'set_scan_status', name='set-scan-status'),
    url(r'^admin/scan/promote-full/(?P<doc_id>\d+)$', 'set_scan_full', name='set-scan-full'),
    url(r'^admin/scan/upload$', 'upload_scan', name='upload-scan'),

    url(r'^test/', include('ipho_exam.urls_test', namespace='test')),

    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)
