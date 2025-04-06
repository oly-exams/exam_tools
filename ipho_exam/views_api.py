from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets

from ipho_exam.models import Document
from ipho_exam.permissions import HasValidApiKeyOrAdmin
from ipho_exam.serializers import DocumentSerializer


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
    filterset_fields = (
        "id",
        "position",
        "participant",
        "barcode_base",
        "num_pages",
    )
