from rest_framework import serializers

from ipho_exam.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    participant = serializers.SlugRelatedField(slug_field="code", read_only=True)

    class Meta:
        model = Document
        fields = "__all__"
