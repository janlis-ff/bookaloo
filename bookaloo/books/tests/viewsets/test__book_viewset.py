import pytest
from django.urls import resolve
from django.urls import reverse_lazy
from rest_framework import status

from bookaloo.books.tests.factories import BookFactory
from bookaloo.books.tests.factories import BookLoanFactory
from bookaloo.books.viewsets import BookViewSet


@pytest.mark.django_db
class TestBookViewSet:
    viewname = "books:books-list"
    url = reverse_lazy(viewname)

    def test__url(self):
        # WHEN / THEN
        assert self.url == "/books/"

    def test__resolved_view_cls(self):
        # WHEN
        resolved = resolve(self.url)

        # THEN
        assert resolved.func.cls == BookViewSet

    @pytest.mark.parametrize(
        argnames=("books_count", "loans_count", "expected_num_queries"),
        argvalues=[
            (1, 1, 4),
            (3, 3, 4),
        ],
    )
    def test__list__num_queries(
        self,
        anonymous_client,
        books_count,
        loans_count,
        expected_num_queries,
        django_assert_num_queries,
    ):
        # GIVEN
        books = BookFactory.create_batch(books_count)
        for book in books:
            BookLoanFactory.create_batch(
                loans_count,
                book_copy__book_edition__book=book,
            )

        # WHEN
        with django_assert_num_queries(expected_num_queries):
            response = anonymous_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
