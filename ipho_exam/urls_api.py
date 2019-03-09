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

from rest_framework.routers import DefaultRouter
from ipho_exam import views_api

router = DefaultRouter()
router.register(r'documents', views_api.DocumentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^schema', views_api.SwaggerSchemaView.as_view(), name='schema'),

    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
