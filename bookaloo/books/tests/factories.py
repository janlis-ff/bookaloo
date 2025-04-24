from datetime import timedelta

from django.utils.timezone import now
from factory import Faker
from factory import LazyAttribute
from factory import Sequence
from factory import SubFactory
from factory.django import DjangoModelFactory

from bookaloo.books import enums
from bookaloo.books import models


class AuthorFactory(DjangoModelFactory):
    full_name = Faker("name")
    birth_year = Faker("year")
    description = Faker("text", max_nb_chars=100)

    class Meta:
        model = models.Author


class PublisherFactory(DjangoModelFactory):
    name = Faker("company")
    address = Faker("address")

    class Meta:
        model = models.Publisher


class BookFactory(DjangoModelFactory):
    title = Faker("sentence", nb_words=4)
    author = SubFactory(AuthorFactory)

    class Meta:
        model = models.Book


class BookEditionFactory(DjangoModelFactory):
    book = SubFactory(BookFactory)
    publisher = SubFactory(PublisherFactory)
    publication_date = Faker("date")
    isbn = Sequence(lambda n: f"12-345-{n:06d}")

    class Meta:
        model = models.BookEdition


class BookCopyFactory(DjangoModelFactory):
    identifier = Sequence(lambda n: str(n).zfill(6))
    book_edition = SubFactory(BookEditionFactory)
    condition = enums.BookCondition.VERY_GOOD
    is_available = True

    class Meta:
        model = models.BookCopy


class BookLoanFactory(DjangoModelFactory):
    book_copy = SubFactory(BookCopyFactory)
    visitor = SubFactory("bookaloo.visitors.tests.factories.VisitorFactory")

    loan_date = LazyAttribute(lambda _: now())
    due_date = LazyAttribute(lambda _: now() + timedelta(days=14))

    class Meta:
        model = models.BookLoan
