from django.conf.urls import patterns, url

from . import views

urlpatterns = [
    #admin urls
    url(r'^admin/$', 'views.AdminOverview', name='adminOverview'),

    #user urls
    url(r'^$', 'views.DelegationOverview', name='DelegationOverview'),
]
