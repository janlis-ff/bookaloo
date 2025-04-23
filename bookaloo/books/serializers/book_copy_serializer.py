from rest_framework import serializers

from bookaloo.books.models import BookCopy


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = "__all__"
        read_only_fields = [
            "id",
            "is_available",
        ]
