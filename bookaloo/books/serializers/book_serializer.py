from rest_framework import serializers

from bookaloo.books.models import Book
from bookaloo.books.serializers.author_serializer import AuthorSerializer


class BookCopiesInlineSerializer(serializers.Serializer):
    total = serializers.IntegerField(source="copies_count_total")
    available = serializers.IntegerField(source="copies_count_available")


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    copies_count = BookCopiesInlineSerializer(
        source="*",
        read_only=True,
    )

    class Meta:
        model = Book
        fields = "__all__"
