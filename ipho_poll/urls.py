from django.conf.urls import patterns, url


urlpatterns = patterns('ipho_poll.views',
    # staff urls
    url(r'^staff/$', 'staffIndex', name='staffIndex'),
    url(r'^staff/question/add$', 'addQuestion', name='addQuestion'),


    #delegation urls
    url(r'^$', 'delegationIndex', name='delegationIndex'),
    url(r'^vote/add$', 'addVote', name='addVote'),
)
