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

from django.urls import path, re_path

from . import views

app_name = "download"
urlpatterns = [
    path("", views.main, {"url": "", "type": "d"}, name="main"),
    re_path(r"add_directory/(?P<url>.*)$", views.add_new_directory, name="add-dir"),
    re_path(r"add_file/(?P<url>.*)$", views.add_new_file, name="add-file"),
    re_path(r"remove/(?P<url>.*)$", views.remove, name="remove"),
    re_path(r"^(?P<type>[fd])/(?P<url>.*)$", views.main, name="path"),
]
