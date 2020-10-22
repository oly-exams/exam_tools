# Exam Tools
#
# Copyright (C) 2014 - 2019 Oly Exams Team
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


from django.conf.urls import include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

from django.contrib.auth import views as auth_views

import ipho_core.views

from . import static_views


urlpatterns = [
    # Examples:
    # url(r'^$', 'exam_tools.views.home', name='home'),
    # url(r'^exam_tools/', include('exam_tools.foo.urls')),
    url(
        r"^$",
        static_views.render_page,
        {
            "p": "pages/home.html",
            "context": {
                "push": settings.ENABLE_PUSH,
                "push_key": settings.PUSH_PUBLIC_KEY,
            },
        },
        name="home",
    ),
    url(r"^exam/", include("ipho_exam.urls")),
    url(r"^poll/", include("ipho_poll.urls")),
    url(r"^marking/", include("ipho_marking.urls")),
    url(r"^print/", include("ipho_print.urls")),
    url(r"^downloads/", include("ipho_download.urls")),
    url(r"^accounts/login/?$", auth_views.login, name="login"),
    url(r"^accounts/logout/?$", auth_views.logout, {"next_page": "/"}, name="logout"),
    url(
        r"^accounts/autologin/(?P<token>[0-9a-z\-]+)/?$",
        ipho_core.views.autologin,
        name="autologin",
    ),
    url(
        r"^accounts/impersonate$", ipho_core.views.list_impersonate, name="impersonate"
    ),
    url(
        r"^accounts/account_request$",
        ipho_core.views.account_request,
        name="account_request",
    ),
    url(
        r"^push/subscription$",
        ipho_core.views.register_push_submission,
        name="push_submission",
    ),
    url(
        r"^push/unsubscribe$", ipho_core.views.delete_push_submission, name="push_unsub"
    ),
    url(r"^push/send$", ipho_core.views.send_push, name="send_push"),
    url(r"^service_worker$", ipho_core.views.service_worker, name="service_worker"),
    url(r"^api/exam/", include("ipho_exam.urls_api")),
    url(r"^easter$", ipho_core.views.random_draw, name="random-draw"),
    url(r"^chocobunny$", ipho_core.views.chocobunny, name="chocobunny"),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    # Uncomment the next line to enable the admin:
    url(r"^admin/", admin.site.urls),
]
