from django.conf.urls import patterns, include, url



urlpatterns = patterns('ipho_exam.views_test',
    url(r'^$', 'index'),
    url(r'^view$', 'view', name='view'),
    url(r'^edit$', 'edit', name='edit'),
    url(r'^inline$', 'inline_edit', name='inline'),
    url(r'^mathquill$', 'mathquill', name='mathquill'),
    url(r'^mathquill_toolbar$', 'mathquill_toolbar', name='mathquill_toolbar'),
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

