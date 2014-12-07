from django.conf.urls import patterns, include, url

urlpatterns = patterns('ipho_editor.views',
    url(r'^$', 'index'),
    url(r'^view$', 'view'),
    url(r'^edit$', 'edit'),
    url(r'^mathquill$', 'mathquill'),
    url(r'^mathquill_toolbar$', 'mathquill_toolbar'),
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

