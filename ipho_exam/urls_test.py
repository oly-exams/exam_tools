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



urlpatterns = patterns('ipho_exam.views_test',
    url(r'^$', 'index'),
    url(r'^view$', 'view', name='view'),
    url(r'^edit$', 'edit', name='edit'),
    url(r'^inline$', 'inline_edit', name='inline'),
    url(r'^mathquill$', 'mathquill', name='mathquill'),
    url(r'^mathquill_toolbar$', 'mathquill_toolbar', name='mathquill_toolbar'),
    # url(r'^(?P<rep_id>\d+)/submit/?$', 'submit'),
)

