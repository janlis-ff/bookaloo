from datetime import timedelta

from django.db import transaction
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiResponse
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from bookaloo.books.serializers import BookLoanSerializer
from bookaloo.books.serializers import BookReturnSerializer


@extend_schema_view(
    post=extend_schema(
        summary=_("Submit a book return"),
        description=_(
            "Allows the user to submit a book return. "
            "The book condition is optional; if not provided, "
            "the book condition will not be updated. "
        ),
        request=BookReturnSerializer,
        responses={
            200: BookLoanSerializer,
            400: OpenApiResponse(
                description=_("Book copy has already been returned"),
            ),
            404: OpenApiResponse(
                description=_("Book copy not found"),
            ),
        },
    ),
)
class BookReturnView(CreateAPIView):
    serializer_class = BookReturnSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        book_loan = serializer.validated_data["book_loan"]
        return Response(
            status=status.HTTP_200_OK,
            data=BookLoanSerializer(book_loan).data,
        )
