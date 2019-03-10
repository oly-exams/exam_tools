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

from . import views_test

urlpatterns = [
    url(r'^$', views_test.index),
    url(r'^view$', views_test.view, name='view'),
    url(r'^edit$', views_test.edit, name='edit'),
    url(r'^inline$', views_test.inline_edit, name='inline'),
    url(r'^mathquill$', views_test.mathquill, name='mathquill'),
    url(r'^mathquill_toolbar$', views_test.mathquill_toolbar, name='mathquill_toolbar'),
]
