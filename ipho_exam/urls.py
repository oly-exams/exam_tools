from django.conf.urls import patterns, include, url


urlpatterns = patterns('ipho_exam.views',
    
    url(r'^$', 'index', name='index'),
    
    url(r'^language/add$', 'add_language', name='language-add'),
    url(r'^language/edit/(?P<lang_id>\d+)$', 'edit_language', name='language-edit'),
    
    url(r'^editor/?$', 'editor'),
    url(r'^editor/(?P<exam_id>\d+)$', 'editor', name='editor-exam'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)$', 'editor', name='editor-question'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)/lang/(?P<lang_id>\d+)?$', 'editor', name='editor-lang'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/orig/(?P<orig_id>\d+)$', 'editor', name='editor-orig'),
    url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/(?P<orig_id>\d+)v(?P<orig_v>\d+)$', 'editor', name='editor-orig-version'),
    # url(r'^editor/(?P<exam_id>\d+)/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)/(?P<orig_id>\d+)v(?P<orig_v1>\d+)v(?P<orig_v2>\d+)?$', 'editor', name='editor-orig-version'),
    
    url(r'^pdf/question/(?P<question_id>\d+)/lang/(?P<lang_id>\d+)?$', 'pdf', name='pdf'),
    
    
    url(r'^test/', include('ipho_exam.urls_test', namespace='test')),
    
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

