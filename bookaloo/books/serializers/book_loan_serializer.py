from datetime import timedelta

from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bookaloo.books.models import Author
from bookaloo.books.models import BookCopy
from bookaloo.books.models import BookLoan
from bookaloo.visitors.models import Visitor


class BookLoanVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = [
            "identifier",
            "full_name",
            "email",
            "phone_number",
        ]


class BookLoanBookAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id",
            "full_name",
            "birth_year",
        ]


class BookLoanBookSerializer(serializers.ModelSerializer):
    book_copy_identifier = serializers.CharField(source="identifier")
    isbn = serializers.CharField(source="book_edition.isbn")
    author = BookLoanBookAuthorSerializer(
        source="book_edition.book.author",
    )

    class Meta:
        model = BookCopy
        fields = [
            "book_copy_identifier",
            "isbn",
            "author",
        ]


class BookLoanSerializer(serializers.ModelSerializer):
    book_copy_identifier = serializers.SlugRelatedField(
        source="book_copy",
        slug_field="identifier",
        queryset=BookCopy.objects.all(),
        write_only=True,
    )
    visitor_identifier = serializers.SlugRelatedField(
        source="visitor",
        slug_field="identifier",
        queryset=Visitor.objects.all(),
        write_only=True,
    )
    due_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )

    book = BookLoanBookSerializer(
        read_only=True,
        source="book_copy",
    )
    visitor = BookLoanVisitorSerializer(read_only=True)
    loan_date = serializers.DateTimeField(read_only=True)

    def validate_due_date(self, value):
        """
        Due date must be at least 1 day ahead.
        """
        if value is None:
            return value
        msg = _("Due date must be at least 1 day ahead.")
        if value <= now() + timedelta(days=1):
            raise serializers.ValidationError(msg)
        return value

    def validate(self, attrs):
        # Ensure that the visitor is active
        if not attrs["visitor"].is_active:
            identifier = attrs["visitor"].identifier
            msg = _("Visitor with identifier=%s is not active.") % identifier
            raise serializers.ValidationError({"visitor_identifier": [msg]})
        # Ensure that the book copy is available
        # NOTE: In case of data discrepancy, we also check for
        #       any current loans for the book copy
        book_copy = attrs["book_copy"]
        active_loans_qs = BookLoan.objects.filter(
            book_copy=book_copy,
            return_date__isnull=True,
        )
        if not book_copy.is_available or active_loans_qs.exists():
            msg = (
                _("Book copy with identifier=%s is not available.")
                % book_copy.identifier
            )
            raise serializers.ValidationError({"book_copy_identifier": [msg]})

        return attrs

    class Meta:
        model = BookLoan
        fields = [
            "id",
            "book_copy_identifier",
            "visitor_identifier",
            "book",
            "visitor",
            "loan_date",
            "due_date",
            "return_date",
        ]
        read_only_fields = ["loan_date", "due_date"]
