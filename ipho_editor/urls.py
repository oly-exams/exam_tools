from django.conf.urls import patterns, include, url

urlpatterns = patterns('ipho_editor.views',
    url(r'^$', 'main'),
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

