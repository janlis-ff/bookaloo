from django.db.models import Count
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from bookaloo.books import models
from bookaloo.books import serializers

DEFAULT_HTTP_METHODS = [
    "head",
    "options",
    "get",
    "post",
    "patch",
    "delete",
]


@extend_schema_view(
    create=extend_schema(summary=_("Create a new author")),
    list=extend_schema(summary=_("List all authors")),
    retrieve=extend_schema(summary=_("Retrieve a specific author")),
    partial_update=extend_schema(summary=_("Partially update a specific author")),
    update=extend_schema(summary=_("Update a specific author")),
    destroy=extend_schema(summary=_("Delete a specific author")),
)
class AuthorViewSet(ModelViewSet):
    queryset = models.Author.objects.all()
    serializer_class = serializers.AuthorSerializer
    filter_backends = [SearchFilter]
    search_fields = ["full_name"]
    http_method_names = DEFAULT_HTTP_METHODS


@extend_schema_view(
    create=extend_schema(summary=_("Create a new publisher")),
    list=extend_schema(summary=_("List all publishers")),
    retrieve=extend_schema(summary=_("Retrieve a specific publisher")),
    partial_update=extend_schema(summary=_("Partially update a specific publisher")),
    update=extend_schema(summary=_("Update a specific publisher")),
    destroy=extend_schema(summary=_("Delete a specific publisher")),
)
class PublisherViewSet(ModelViewSet):
    queryset = models.Publisher.objects.all()
    serializer_class = serializers.PublisherSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "address"]
    http_method_names = DEFAULT_HTTP_METHODS


@extend_schema_view(
    create=extend_schema(summary=_("Create a new book")),
    list=extend_schema(summary=_("List all books")),
    retrieve=extend_schema(summary=_("Retrieve a specific book")),
    partial_update=extend_schema(summary=_("Partially update a specific book")),
    update=extend_schema(summary=_("Update a specific book")),
    destroy=extend_schema(summary=_("Delete a specific book")),
)
class BookViewSet(ModelViewSet):
    serializer_class = serializers.BookSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "author__full_name"]
    http_method_names = DEFAULT_HTTP_METHODS

    def get_queryset(self):
        return models.Book.objects.select_related(
            "author",
        ).annotate(
            copies_count_total=Count("editions__copies"),
            copies_count_available=Count(
                "editions__copies",
                filter=Q(editions__copies__is_available=True),
            ),
        )


@extend_schema_view(
    create=extend_schema(summary=_("Create a new book edition")),
    list=extend_schema(summary=_("List all book editions")),
    retrieve=extend_schema(summary=_("Retrieve a specific book edition")),
    partial_update=extend_schema(summary=_("Partially update a specific book edition")),
    update=extend_schema(summary=_("Update a specific book edition")),
    destroy=extend_schema(summary=_("Delete a specific book edition")),
)
class BookEditionViewSet(ModelViewSet):
    queryset = models.BookEdition.objects.all()
    serializer_class = serializers.BookEditionSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "isbn",
        "book__title",
        "publisher__name",
        "book__author__full_name",
    ]
    http_method_names = DEFAULT_HTTP_METHODS


@extend_schema_view(
    create=extend_schema(summary=_("Create a new book copy")),
    list=extend_schema(summary=_("List all book copies")),
    retrieve=extend_schema(summary=_("Retrieve a specific book copy")),
    partial_update=extend_schema(summary=_("Partially update a specific book copy")),
    update=extend_schema(summary=_("Update a specific book copy")),
    destroy=extend_schema(summary=_("Delete a specific book copy")),
)
class BookCopyViewSet(ModelViewSet):
    queryset = models.BookCopy.objects.all()
    serializer_class = serializers.BookCopySerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "identifier",
        "book_edition__isbn",
        "book_edition__book__title",
        "book_edition__book__author__full_name",
        "book_edition__publisher__name",
    ]
    http_method_names = DEFAULT_HTTP_METHODS
