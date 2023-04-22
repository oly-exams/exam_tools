# Exam Tools
#
# Copyright (C) 2014 - 2021 Oly Exams Team
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

from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from ipho_exam import views_api
from ipho_exam.permissions import HasValidApiKeyOrAdmin


router = DefaultRouter()
router.register(r"documents", views_api.DocumentViewSet)

app_name = "api-exam"
urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(
        r"^api-schema/",
        SpectacularAPIView.as_view(
            permission_classes=[
                HasValidApiKeyOrAdmin,
            ],
        ),
        name="schema-api",
    ),
    re_path(
        r"^schema",
        SpectacularSwaggerView.as_view(url_name="api-exam:schema-api"),
        name="schema",
    ),
    # re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
