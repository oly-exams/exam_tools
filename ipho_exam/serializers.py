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

from rest_framework import serializers
from ipho_exam.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='code', read_only=True)
    exam = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
