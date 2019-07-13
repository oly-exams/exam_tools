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

from builtins import object
from .exceptions import IphoExamException


class IphoExamExceptionsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, IphoExamException):
            return exception.response


class CheckUserAgentMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        import re
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_api_call = request.path.startswith('/api')
        fmatch = re.search(r'Firefox/([0-9]*).', user_agent)
        if fmatch and int(fmatch.group(1)) >= 50:
            is_Firefox_50_or_more = True
        else:
            is_Firefox_50_or_more = False
        cmatch = re.search(r'Chrome/([0-9]*)', user_agent)
        if cmatch and int(cmatch.group(1)) >= 60:
            is_Chrome_60_or_more = True
        else:
            is_Chrome_60_or_more = False
        is_letsencrypt = 'letsencrypt' in user_agent or 'certbot' in user_agent
        if not (is_Firefox_50_or_more or is_Chrome_60_or_more or is_letsencrypt or request.user.is_superuser or is_api_call):
            from django.shortcuts import render
            return render(request, 'pages/unsupported_browser.html')
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
