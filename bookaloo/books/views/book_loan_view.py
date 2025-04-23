from datetime import timedelta

from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.generics import ListCreateAPIView

from bookaloo.books.models import BookLoan
from bookaloo.books.serializers import BookLoanSerializer


@extend_schema_view(
    post=extend_schema(
        summary=_("Submit a new book loan"),
        description=_(
            "Allows the user to submit a new book loan. "
            "The user must provide the book copy identifier "
            "and the library visitor's card number (identifier). "
            "Due date is optional; if not provided, it will be set "
            "to 2 weeks from the current date."
        ),
    ),
)
class BookLoanView(ListCreateAPIView):
    serializer_class = BookLoanSerializer

    def get_queryset(self):
        return BookLoan.objects.select_related(
            "visitor",
            "book_copy__book_edition__book__author",
        )

    @transaction.atomic
    def perform_create(self, serializer):
        data = serializer.validated_data
        if data.get("due_date", None) is None:
            due_date = now() + timedelta(weeks=2)
            serializer.validated_data["due_date"] = due_date
        super().perform_create(serializer)
        data["book_copy"].is_available = False
        data["book_copy"].save()
