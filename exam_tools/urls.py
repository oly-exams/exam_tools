# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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


from django.urls import include, path, re_path
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

from django.contrib.auth import views as auth_views

import ipho_core.views

from . import static_views


urlpatterns = [
    # Examples:
    # re_path(r'^$', 'exam_tools.views.home', name='home'),
    # re_path(r'^exam_tools/', include('exam_tools.foo.urls')),
    path(
        "",
        static_views.render_page,
        {
            "p": "pages/home.html",
            "context": {
                "push": settings.ENABLE_PUSH,
                "push_key": settings.PUSH_PUBLIC_KEY,
                "control_show_phases": settings.CONTROL_SHOW_PHASES_ON_HOME,
            },
        },
        name="home",
    ),
    path("control/", include("ipho_control.urls")),
    path("exam/", include("ipho_exam.urls")),
    path("poll/", include("ipho_poll.urls")),
    path("marking/", include("ipho_marking.urls")),
    path("print/", include("ipho_print.urls")),
    path("downloads/", include("ipho_download.urls")),
    re_path(r"^accounts/login/?$", auth_views.LoginView.as_view(), name="login"),
    re_path(
        r"^accounts/logout/?$",
        auth_views.LogoutView.as_view(next_page="/"),
        name="logout",
    ),
    re_path(
        r"^accounts/autologin/(?P<token>[0-9a-z\-]+)/?$",
        ipho_core.views.autologin,
        name="autologin",
    ),
    path(
        "accounts/impersonate/",
        ipho_core.views.list_impersonate,
        name="list_impersonate",
    ),
    path(
        "accounts/impersonate/<int:pk>/",
        ipho_core.views.impersonate,
        name="impersonate",
    ),
    path(
        "accounts/impersonate_stop/",
        ipho_core.views.impersonate_stop,
        name="impersonate_stop",
    ),
    path(
        "accounts/account_request",
        ipho_core.views.account_request,
        name="account_request",
    ),
    path(
        "push/subscription",
        ipho_core.views.register_push_submission,
        name="push_submission",
    ),
    path("push/unsubscribe", ipho_core.views.delete_push_submission, name="push_unsub"),
    path("push/send", ipho_core.views.send_push, name="send_push"),
    path("service_worker", ipho_core.views.service_worker, name="service_worker"),
    path("api/exam/", include("ipho_exam.urls_api")),
    path("easter", ipho_core.views.random_draw, name="random-draw"),
    path("chocobunny", ipho_core.views.chocobunny, name="chocobunny"),
    # Uncomment the admin/doc line below to enable admin documentation:
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    # Uncomment the next line to enable the admin:
    path("admin/", admin.site.urls),
]
