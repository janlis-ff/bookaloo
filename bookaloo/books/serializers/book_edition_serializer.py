from rest_framework import serializers

from bookaloo.books.models import BookEdition


class BookEditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookEdition
        fields = "__all__"
