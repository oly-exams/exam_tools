# Exam Tools
#
# Copyright (C) 2014 - 2017 Oly Exams Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import static_views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'exam_tools.views.home', name='home'),
    # url(r'^exam_tools/', include('exam_tools.foo.urls')),

    url(r'^/?$', static_views.render_page, {'p' : 'pages/home.html'}, name='home'),
    url(r'^exam/', include('ipho_exam.urls', namespace='exam')),
    url(r'^poll/', include('ipho_poll.urls', namespace='poll')),
    url(r'^marking/', include('ipho_marking.urls', namespace='marking')),
    url(r'^print/', include('ipho_print.urls', namespace='print')),
    url(r'^downloads/', include('ipho_download.urls', namespace='download')),

    url(r'^accounts/login/?$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/?$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    url(r'^accounts/autologin/(?P<token>[0-9a-z\-]+)/?$', 'ipho_core.views.autologin', name='autologin'),
    url(r'^accounts/impersonate$', 'ipho_core.views.list_impersonate', name='impersonate'),


    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
