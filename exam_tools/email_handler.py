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
from django.utils.log import AdminEmailHandler

class EnhancedAdminEmailHandler(AdminEmailHandler):
    def emit(self, record):
        self.current_record = record
        super().emit(record)
    def send_mail(self, subject, message, *args, **kwargs):
        # Let's be a bit defensive here, it'd be bad to have errors in this method...
        # (for reasons, see title text of xkcd.com/1163)
        if hasattr(self, "current_record") and hasattr(self.current_record, "request"):
            request = self.current_record.request
            if hasattr(request, "user") and hasattr(request.user, "is_authenticated") and request.user.is_authenticated:
                additional_info = "\n  Username: " + request.user.username
            else:
                additional_info = "\n  Unauthenticated user"
        else:
            additional_info = "\n  Additional info: unavailable"
        super().send_mail(subject, message + additional_info, *args, **kwargs)
