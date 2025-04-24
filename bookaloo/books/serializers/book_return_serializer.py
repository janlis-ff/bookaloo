from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from bookaloo.books.enums import BookCondition
from bookaloo.books.models import BookCopy
from bookaloo.books.models import BookLoan


class BookReturnSerializer(serializers.ModelSerializer):
    book_copy_condition = serializers.ChoiceField(
        choices=BookCondition.choices,
        required=False,
        allow_null=True,
        help_text=_("Condition of the book while being returned."),
        write_only=True,
    )
    book_copy_identifier = serializers.SlugRelatedField(
        source="book_copy",
        slug_field="identifier",
        queryset=BookCopy.objects.all(),
        help_text=_("Identifier of the book being returned."),
        write_only=True,
    )

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        try:
            book_loan = BookLoan.objects.get(
                book_copy=internal_value["book_copy"],
                return_date__isnull=True,
            )
        except BookLoan.DoesNotExist as e:
            msg = _("That book copy has already been returned.")
            raise serializers.ValidationError({"book_copy_identifier": [msg]}) from e
        internal_value["book_loan"] = book_loan
        return internal_value

    def save(self, **kwargs):
        book_loan = self.validated_data["book_loan"]
        book_copy = book_loan.book_copy
        book_loan.return_date = now()
        book_copy.is_available = True
        book_copy.condition = (
            self.validated_data.get(
                "book_copy_condition",
                None,
            )
            or book_copy.condition
        )
        book_loan.save()
        book_copy.save()

    class Meta:
        model = BookLoan
        fields = [
            "book_copy_identifier",
            "book_copy_condition",
        ]
