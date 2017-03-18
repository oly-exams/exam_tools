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

from ipho_exam.models import Document
from ipho_exam.serializers import DocumentSerializer
from rest_framework import generics, viewsets

from ipho_exam.permissions import HasValidApiKeyOrAdmin

class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    Access and edit the collection of student documents (exam printouts and scans)

    list:
        param1 -- First test
        param2 -- Second

    retrieve: Single entry.
    """
    permission_classes = (HasValidApiKeyOrAdmin,)
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
