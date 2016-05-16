from django.conf.urls import patterns, include, url


urlpatterns = patterns('ipho_exam.views',

    url(r'^/?$', 'index', name='index'),
    url(r'^wizard$', 'wizard', name='wizard'),
    url(r'^main$', 'main', name='main'),

    url(r'^translation/list/?$', 'translations_list', name='list'),
    url(r'^translation/add/(?P<exam_id>\d+)$', 'add_translation', name='add-translation'),
    url(r'^translation/upload/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)$', 'add_pdf_node', name='upload-translation'),
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
    url(r'^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'compiled_question', {'raw_tex': True}, name='tex'),
    url(r'^pdf/exam/(?P<exam_id>\d+)/student/(?P<student_id>\d+)$', 'pdf_exam_for_student', name='pdf-exam-student'),

    url(r'^pdf-task/(?P<token>[0-9a-z\-]+)$', 'pdf_task', name='pdf-task'),
    url(r'^pdf-task/(?P<token>[0-9a-z\-]+)/status$', 'pdf_task_status', name='pdf-task-status'),

    url(r'^feedbacks/list/?$', 'feedbacks_list', name='feedbacks-list'),
    url(r'^feedbacks/add/(?P<exam_id>\d+)$', 'feedbacks_add', name='feedbacks-add'),

    url(r'^submission/list$', 'submission_exam_list', name='submission-exam-list'),
    url(r'^submission/(?P<exam_id>\d+)/assign$', 'submission_exam_assign', name='submission-exam-assign'),
    url(r'^submission/(?P<exam_id>\d+)/confirm$', 'submission_exam_confirm', name='submission-exam-confirm'),
    url(r'^submission/(?P<exam_id>\d+)/submitted$', 'submission_exam_submitted', name='submission-exam-submitted'),

    url(r'^figures/?$', 'figure_list', name='figures'),
    url(r'^figure/add$', 'figure_add', name='figure-add'),
    url(r'^figure/(?P<fig_id>\d+)$', 'figure_edit', name='figure-edit'),
    url(r'^figure/(?P<fig_id>\d+)/remove$', 'figure_delete', name='figure-delete'),
    url(r'^figure/(?P<fig_id>\d+)/export.svg$', 'figure_export', {'output_format': 'svg'}, name='figure-export'),
    url(r'^figure/(?P<fig_id>\d+)/export.pdf$', 'figure_export', {'output_format': 'pdf'}, name='figure-export-pdf'),
    url(r'^figure/(?P<fig_id>\d+)/(?P<lang_id>\d+)/export.svg$', 'figure_export', {'output_format': 'svg'}, name='figure-lang-export'),
    url(r'^figure/(?P<fig_id>\d+)/(?P<lang_id>\d+)/export.pdf$', 'figure_export', {'output_format': 'pdf'}, name='figure-lang-export-pdf'),

    url(r'^admin/?$', 'admin_list', name='admin'),
    url(r'^admin/(?P<exam_id>\d+)/sort$', 'admin_sort', name='admin-sort'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/newversion$', 'admin_new_version', name='admin-new-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/accept$', 'admin_accept_version', name='admin-accept-version'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<compare_version>\d+)/v(?P<version_num>\d+)/accept$', 'admin_accept_version', name='admin-accept-version-diff'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor$', 'admin_editor', name='admin-editor'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/edit/(?P<block_id>\w+)$', 'admin_editor_block', name='admin-editor-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/delete/(?P<block_id>\w+)$', 'admin_editor_delete_block', name='admin-editor-delete-block'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/v(?P<version_num>\d+)/editor/block/add/(?P<block_id>\w+)/(?P<tag_name>\w+)$', 'admin_editor_add_block', name='admin-editor-add-block'),

    url(r'^admin/submissions/list/(?P<exam_id>\d+)$', 'admin_submission_list', name='admin-submission-list'),
    url(r'^admin/submissions/assign/(?P<exam_id>\d+)$', 'admin_submission_assign', name='admin-submission-assign'),
    url(r'^admin/submissions/(?P<submission_id>\d+)/delete$', 'admin_submission_delete', name='admin-submission-delete'),

    url(r'^test/', include('ipho_exam.urls_test', namespace='test')),

    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)
