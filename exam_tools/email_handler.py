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

from django.conf import settings
from django.utils.encoding import force_text
from django.views.debug import ExceptionReporter, get_exception_reporter_filter
from django.utils.log import AdminEmailHandler

from copy import copy


class EnhancedAdminEmailHandler(AdminEmailHandler):
    # NOTE: most of this directly copied from AdminEmailHandler.

    def __init__(self, *args, **kwargs):
        super(EnhancedAdminEmailHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        request_repr = "Unavailable"
        user_info = "Unavailable"

        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 else 'EXTERNAL'),
                record.getMessage()
            )

            filter = get_exception_reporter_filter(request)
            request_repr = '\n{}'.format(force_text(filter.get_request_repr(request)))

            if request.user.is_authenticated:
                user_info = "\n  Username: " + request.user.username
            else:
                user_info = "\n  Unauthenticated user"
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None

        subject = self.format_subject(subject)

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = ExceptionReporter(request, is_email=True, *exc_info)
        message = "%s\n\n%s\n\n%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text(), request_repr, user_info)
        html_message = reporter.get_traceback_html() if self.include_html else None
        self.send_mail(subject, message, fail_silently=True, html_message=html_message)
