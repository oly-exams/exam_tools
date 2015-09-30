from django.conf.urls import patterns, include, url


urlpatterns = patterns('ipho_exam.views',

    url(r'^$', 'index', name='index'),
    url(r'^translation/list/?$', 'list', name='list'),
    url(r'^translation/add/(?P<exam_id>\d+)$', 'add_translation', name='add-translation'),

    url(r'^language/add$', 'add_language', name='language-add'),
    url(r'^language/edit/(?P<lang_id>\d+)$', 'edit_language', name='language-edit'),

    url(r'^editor/?$', 'editor'),
    url(r'^editor/(?P<exam_id>\d+)$', 'editor', name='editor-exam'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$', 'editor', name='editor-question'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)$', 'editor', name='editor-orig'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)/lang/(?P<lang_id>\d+)?$', 'editor', name='editor-orig-lang'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)$', 'editor', name='editor-origdiff'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig_diff/(?P<orig_id>\d+)v(?P<orig_diff>\d+)/lang/(?P<lang_id>\d+)?$', 'editor', name='editor-origdiff-lang'),

    url(r'^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'pdf', name='pdf'),
    url(r'^tex/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'pdf', {'raw_tex': True}, name='tex'),

    url(r'^figures/?$', 'figure_list', name='figures'),
    url(r'^figure/add$', 'figure_add', name='figure-add'),
    url(r'^figure/(?P<fig_id>\d+)$', 'figure_edit', name='figure-edit'),
    url(r'^figure/(?P<fig_id>\d+)/export.svg$', 'figure_export', {'output_format': 'svg'}, name='figure-export'),
    url(r'^figure/(?P<fig_id>\d+)/export.pdf$', 'figure_export', {'output_format': 'pdf'}, name='figure-export-pdf'),

    url(r'^admin/?$', 'admin_list', name='admin'),
    url(r'^admin/(?P<exam_id>\d+)/sort$', 'admin_sort', name='admin-sort'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/props$', 'admin_props', name='admin-props'),
    url(r'^admin/(?P<exam_id>\d+)/(?P<question_id>\d+)/editor$', 'admin_editor', name='admin-editor'),

    url(r'^test/', include('ipho_exam.urls_test', namespace='test')),

    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)
