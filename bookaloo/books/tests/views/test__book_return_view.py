import pytest
from django.urls import resolve
from django.urls import reverse_lazy
from django.utils.timezone import now
from freezegun import freeze_time
from rest_framework import status

from bookaloo.books.enums import BookCondition
from bookaloo.books.tests.factories import BookCopyFactory
from bookaloo.books.tests.factories import BookLoanFactory
from bookaloo.books.views import BookReturnView


@pytest.mark.django_db
class TestBookReturnView:
    viewname = "books:book-returns"
    url = reverse_lazy(viewname)

    def test__url(self):
        # WHEN / THEN
        assert self.url == "/books/returns"

    def test__resolved_view_cls(self):
        # WHEN
        resolved = resolve(self.url)

        # THEN
        assert resolved.func.cls == BookReturnView

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
        }

    def test__book_copy_not_found(self, anonymous_client):
        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": "123456",
            },
        )

        # THEN
        expected_msg = "Object with identifier=123456 does not exist."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"book_copy_identifier": [expected_msg]}

    @pytest.mark.parametrize(
        "book_loan_exists",
        [True, False],
    )
    def test__book_copy_already_returned(self, anonymous_client, book_loan_exists):
        # GIVEN
        book_copy = BookCopyFactory()
        if book_loan_exists:
            BookLoanFactory(
                book_copy=book_copy,
                return_date=now(),
            )

        # WHEN
        response = anonymous_client.post(
            self.url,
            data={
                "book_copy_identifier": book_copy.identifier,
            },
        )

        # THEN
        expected_msg = "That book copy has already been returned."
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"book_copy_identifier": [expected_msg]}

    @freeze_time("2020-01-01")
    @pytest.mark.parametrize(
        argnames=("extra_params", "expected_book_condition"),
        argvalues=[
            pytest.param(
                {},
                BookCondition.VERY_GOOD,
                id="no_book_condition",
            ),
            pytest.param(
                {"book_copy_condition": None},
                BookCondition.VERY_GOOD,
                id="book_condition_none",
            ),
            pytest.param(
                {"book_copy_condition": BookCondition.POOR},
                BookCondition.POOR,
                id="book_condition_worsened",
            ),
        ],
    )
    def test__success(self, anonymous_client, extra_params, expected_book_condition):
        # GIVEN
        book_copy = BookCopyFactory(is_available=False)
        book_loan = BookLoanFactory(
            book_copy=book_copy,
            return_date=None,
        )
        author = book_copy.book_edition.book.author
        visitor = book_loan.visitor

        # WHEN
        with freeze_time("2020-01-10"):
            response = anonymous_client.post(
                self.url,
                data={
                    "book_copy_identifier": book_copy.identifier,
                    **extra_params,
                },
                format="json",
            )
        book_copy.refresh_from_db()
        book_loan.refresh_from_db()

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": book_loan.id,
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
            "return_date": "2020-01-10T00:00:00Z",
        }
        assert book_copy.is_available is True
        assert book_copy.condition == expected_book_condition
        assert book_loan.return_date is not None
