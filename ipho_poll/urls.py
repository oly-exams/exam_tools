from django.conf.urls import patterns, url


urlpatterns = patterns('ipho_poll.views',
    # staff urls
    url(r'^staff/$', 'staffIndex', name='staffIndex'),

    url(r'^question/add/$', 'addQuestion', name='addQuestion'),
    url(r'^question/(?P<question_pk>\d+)/delete/$', 'deleteQuestion', name='deleteQuestion'),
    url(r'^question/(?P<question_pk>\d+)/edit/$', 'editQuestion', name='editQuestion'),
    url(r'^question/(?P<question_pk>\d+)/$', 'setEndDate', name='setEndDate'),

    #delegation urls
    url(r'^$', 'voterIndex', name='voterIndex'),
)
