# Exam Tools
#
# Copyright (C) 2014 - 2023 Oly Exams Team
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

import os
from django.conf import settings


def ipho_context(request):
    favicons_path = "favicons"
    default_favicon_path = os.path.join(favicons_path, "default")
    favicon_path = default_favicon_path
    if any("secret" in hostname for hostname in settings.ALLOWED_HOSTS):
        favicon_path = os.path.join(favicons_path, "secret")
    if any(
        partial_name in hostname
        for hostname in settings.ALLOWED_HOSTS
        for partial_name in ["dev", "test"]
    ):
        favicon_path = os.path.join(favicons_path, "dev")
    return {
        "DEMO_MODE": settings.DEMO_MODE,
        "DEMO_SIGN_UP": settings.DEMO_SIGN_UP,
        "VERSION": settings.VERSION,
        "VERSION_DATE": settings.VERSION_DATE,
        "DOCS_URL": settings.DOCS_URL,
        "STATIC_PATH": settings.STATIC_PATH,
        "DEBUG": getattr(settings, "DEBUG", False),
        "OFFICIALLY_SUPPORTED": settings.OFFICIALLY_SUPPORTED,
        "FAVICON_PATH": favicon_path,
    }
