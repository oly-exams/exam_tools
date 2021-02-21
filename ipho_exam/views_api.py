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


from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, mixins

from ipho_exam.models import Document
from ipho_exam.serializers import DocumentSerializer
from ipho_exam.permissions import HasValidApiKeyOrAdmin


class DocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    # """
    # Access and edit the collection of participant documents (exam printouts and scans)
    # """
    """
    list: Collection of documents
    retrieve: Single entry
    partial_update: Partially update single entry
    update: Update single entry
    """
    permission_classes = (HasValidApiKeyOrAdmin,)
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = (
        "id",
        "position",
        "participant",
        "barcode_base",
        "num_pages",
    )
