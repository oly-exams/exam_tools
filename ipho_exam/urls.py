from django.conf.urls import patterns, include, url



urlpatterns = patterns('ipho_exam.views',
    
    url(r'^$', 'index', name='index'),
    
    
    url(r'^test/', include('ipho_exam.urls_test', namespace='test')),
    
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

