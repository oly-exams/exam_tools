from django.conf.urls import patterns, url


urlpatterns = patterns('ipho_poll.views',
    # urls
    url(r'^staff/$', 'staffIndex', name='staffIndex'),
    url(r'^staff/question/add$', 'addQuestion', name='addQuestion'),


    #user urls
    url(r'^$', 'delegationIndex', name='delegationIndex'),
)
