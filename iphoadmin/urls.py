from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import static_views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'iphoadmin.views.home', name='home'),
    # url(r'^iphoadmin/', include('iphoadmin.foo.urls')),
    
    url(r'^/?$', static_views.render_page, {'p' : 'pages/home.html'}, name='home'),
    url(r'^exam/', include('ipho_exam.urls', namespace='exam')),
    
    (r'^accounts/login/?$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/?$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    
    
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
