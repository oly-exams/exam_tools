from django.conf.urls import patterns, url


urlpatterns = patterns('ipho_poll.views',
    #admin urls
    url(r'^admin/$', 'adminIndex', name='adminIndex'),

    #user urls
    url(r'^$', 'delegationIndex', name='delegationIndex'),
)
