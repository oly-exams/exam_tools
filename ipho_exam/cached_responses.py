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

from django.http import HttpResponse, Http404, HttpResponseNotModified, HttpResponseRedirect
from django.core.urlresolvers import reverse

from hashlib import md5

from ipho_exam import pdf, tasks


def compile_tex(request, body, ext_resources=[], filename='question.pdf'):
    etag = md5(body).hexdigest()
    if request.META.get('HTTP_IF_NONE_MATCH', '') == etag:
        return HttpResponseNotModified()

    job = tasks.compile_tex.delay(body, ext_resources, filename, etag)
    return HttpResponseRedirect(reverse('exam:pdf-task', args=[job.id]))
