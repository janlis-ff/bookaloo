import pytest
from django.urls import resolve
from django.urls import reverse_lazy
from freezegun import freeze_time
from rest_framework import status

from bookaloo.books.tests.factories import BookCopyFactory
from bookaloo.books.tests.factories import BookLoanFactory
from bookaloo.books.views import BookLoanView
from bookaloo.visitors.tests.factories import VisitorFactory


@pytest.mark.django_db
class TestBookLoanView:
    viewname = "books:book-loans"
    url = reverse_lazy(viewname)

    def test__url(self):
        # WHEN / THEN
        assert self.url == "/books/loans"

    def test__resolved_view_cls(self):
        # WHEN
        resolved = resolve(self.url)

        # THEN
        assert resolved.func.cls == BookLoanView

    def test__create__required_params(self, anonymous_client):
        # WHEN
        response = anonymous_client.post(
            self.url,
            data={},
        )

        # THEN
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "book_copy_identifier": ["This field is required."],
            "visitor_identifier": ["This field is required."],
        }

    def test__book_copy_not_found(self, anonymous_client):
        # GIVEN
        visitor = VisitorFactory()

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": "123456",
                "visitor_identifier": visitor.identifier,
            },
        )

        # THEN
        expected_msg = "Object with identifier=123456 does not exist."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"book_copy_identifier": [expected_msg]}

    def test__visitor_not_found(self, anonymous_client):
        # GIVEN
        book_copy = BookCopyFactory()

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
                "visitor_identifier": "123456",
            },
        )

        # THEN
        expected_msg = "Object with identifier=123456 does not exist."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"visitor_identifier": [expected_msg]}

    def test__visitor_not_active(self, anonymous_client):
        # GIVEN
        book_copy = BookCopyFactory()
        visitor = VisitorFactory(is_active=False)

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
                "visitor_identifier": visitor.identifier,
            },
        )

        # THEN
        expected_msg = f"Visitor with identifier={visitor.identifier} is not active."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"visitor_identifier": [expected_msg]}

    def test__book_copy__not_available(self, anonymous_client):
        # GIVEN
        book_copy = BookCopyFactory(is_available=False)
        visitor = VisitorFactory()

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
                "visitor_identifier": visitor.identifier,
            },
        )

        # THEN
        expected_msg = (
            f"Book copy with identifier={book_copy.identifier} is not available."
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"book_copy_identifier": [expected_msg]}

    def test__book_copy__data_discrepancy(self, anonymous_client):
        """
        In case the book copy is "available", but an active
        loan exists, the API should still return a 400 error.
        """
        # GIVEN
        book_copy = BookCopyFactory(is_available=True)
        visitor = VisitorFactory()
        BookLoanFactory(
            book_copy=book_copy,
            visitor=visitor,
            return_date=None,
        )

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
                "visitor_identifier": visitor.identifier,
            },
        )

        # THEN
        expected_msg = (
            f"Book copy with identifier={book_copy.identifier} is not available."
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"book_copy_identifier": [expected_msg]}

    @pytest.mark.parametrize(
        argnames=("extra_params", "expected_due_date"),
        argvalues=[
            pytest.param(
                {},
                "2020-01-15T00:00:00Z",
                id="no_due_date",
            ),
            pytest.param(
                {"due_date": None},
                "2020-01-15T00:00:00Z",
                id="due_date_none",
            ),
            pytest.param(
                {"due_date": "2020-01-20T15:30:00Z"},
                "2020-01-20T15:30:00Z",
                id="due_date_provided",
            ),
        ],
    )
    @freeze_time("2020-01-01")
    def test__create__success(self, anonymous_client, extra_params, expected_due_date):
        # GIVEN
        book_copy = BookCopyFactory()
        visitor = VisitorFactory()
        author = book_copy.book_edition.book.author

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
                "visitor_identifier": visitor.identifier,
                **extra_params,
            },
            format="json",
        )
        book_copy.refresh_from_db()
        created_obj = book_copy.loans.get()

        # THEN
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json() == {
            "id": created_obj.pk,
            "book": {
                "book_copy_identifier": book_copy.identifier,
                "isbn": book_copy.book_edition.isbn,
                "author": {
                    "id": author.id,
                    "full_name": author.full_name,
                    "birth_year": int(author.birth_year),
                },
            },
            "visitor": {
                "identifier": visitor.identifier,
                "full_name": visitor.full_name,
                "email": visitor.email,
                "phone_number": visitor.phone_number,
            },
            "loan_date": "2020-01-01T00:00:00Z",
            "due_date": expected_due_date,
            "return_date": None,
        }
        assert book_copy.is_available is False

    @freeze_time("2020-01-01")
    def test__list__response(self, anonymous_client):
        # GIVEN
        book_loan = BookLoanFactory()
        book_copy = book_loan.book_copy
        author = book_copy.book_edition.book.author
        visitor = book_loan.visitor

        # WHEN
        response = anonymous_client.get(self.url)

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": book_loan.pk,
                    "book": {
                        "book_copy_identifier": book_copy.identifier,
                        "isbn": book_copy.book_edition.isbn,
                        "author": {
                            "id": author.id,
                            "full_name": author.full_name,
                            "birth_year": int(author.birth_year),
                        },
                    },
                    "visitor": {
                        "identifier": visitor.identifier,
                        "full_name": visitor.full_name,
                        "email": visitor.email,
                        "phone_number": visitor.phone_number,
                    },
                    "loan_date": "2020-01-01T00:00:00Z",
                    "due_date": "2020-01-15T00:00:00Z",
                    "return_date": None,
                }
            ],
        }

    @pytest.mark.parametrize(
        argnames=("num_loans", "expected_num_queries"),
        argvalues=[
            (1, 4),
            (5, 4),
        ],
    )
    def test__list__num_queries(
        self,
        anonymous_client,
        num_loans,
        expected_num_queries,
        django_assert_num_queries,
    ):
        # GIVEN
        BookLoanFactory.create_batch(num_loans)

        # WHEN / THEN
        with django_assert_num_queries(expected_num_queries):
            response = anonymous_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
