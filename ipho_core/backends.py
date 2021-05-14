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

from ipho_core.models import User


class TokenLoginBackend:
    def authenticate(self, request, token=None):  # pylint: disable=no-self-use
        if token is None:
            return None
        try:
            user = User.objects.get(autologin__token=token)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):  # pylint: disable=no-self-use
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
