# Exam Tools
#
# Copyright (C) 2014 - 2018 Oly Exams Team
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

from django.http import HttpResponseForbidden
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class IphoExamException(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return u'IPhO Exam Exception. Reponse: {}'.format(self.response)


class IphoExamForbidden(Exception):
    def __init__(self, msg):
        super(IphoExamForbidden, self).__init__(HttpResponseForbidden(msg))
