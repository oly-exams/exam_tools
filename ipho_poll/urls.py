from django.conf.urls import patterns, url


urlpatterns = patterns('ipho_poll.views',
    #admin urls
    url(r'^admin/$', 'adminOverview', name='adminOverview'),

    #user urls
    url(r'^$', 'delegationOverview', name='DelegationOverview'),
)
