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

from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view
from ipho_exam import views_api

router = DefaultRouter()
router.register(r'documents', views_api.DocumentViewSet)

schema_view = get_swagger_view(title='Exam Tools - Exam Documents API')

urlpatterns = patterns('ipho_exam.views_api',
    url(r'^', include(router.urls)),
    url(r'^docs/', schema_view),

    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
