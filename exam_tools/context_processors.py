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

from django.conf import settings

def ipho_context(request):
    return {
        'DEMO_MODE': settings.DEMO_MODE,
        'VERSION': settings.VERSION,
        'VERSION_DATE': settings.VERSION_DATE,
        'DOCS_URL': settings.DOCS_URL,
        'STATIC_PATH': settings.STATIC_PATH,
    }
