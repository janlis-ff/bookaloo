import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from bookaloo.books.enums import BookCondition
from bookaloo.books.tests.factories import AuthorFactory
from bookaloo.books.tests.factories import BookCopyFactory
from bookaloo.books.tests.factories import BookEditionFactory
from bookaloo.books.tests.factories import BookFactory
from bookaloo.books.tests.factories import BookLoanFactory
from bookaloo.books.tests.factories import PublisherFactory


class Command(BaseCommand):
    help = _("Generate test data for API testing purposes")

    books_data = {
        "J.R.R. Tolkien": [
            "The Hobbit",
            "The Fellowship of the Ring",
            "The Two Towers",
            "The Return of the King",
        ],
        "George R.R. Martin": [
            "A Game of Thrones",
            "A Clash of Kings",
            "A Storm of Swords",
            "A Feast for Crows",
            "A Dance with Dragons",
        ],
        "J.K. Rowling": [
            "Harry Potter and the Philosopher's Stone",
            "Harry Potter and the Chamber of Secrets",
            "Harry Potter and the Prisoner of Azkaban",
            "Harry Potter and the Goblet of Fire",
            "Harry Potter and the Order of the Phoenix",
            "Harry Potter and the Half-Blood Prince",
            "Harry Potter and the Deathly Hallows",
        ],
        "C.S. Lewis": [
            "The Lion, the Witch and the Wardrobe",
            "Prince Caspian",
            "The Voyage of the Dawn Treader",
        ],
        "Isaac Asimov": [
            "Foundation",
            "Foundation and Empire",
            "Second Foundation",
            "Foundation's Edge",
            "Foundation and Earth",
        ],
        "Michael Scott": [
            "Somehow, I Manage",
            "100 Inspirational Quotes",
        ],
        "Arthur C. Clarke": [
            "2001: A Space Odyssey",
            "Rendezvous with Rama",
            "The Fountains of Paradise",
            "The City and the Stars",
        ],
        "Philip K. Dick": [
            "Do Androids Dream of Electric Sheep?",
        ],
        "Ray Bradbury": [
            "Fahrenheit 451",
            "The Martian Chronicles",
            "Something Wicked This Way Comes",
        ],
        "Jan J.L.": [
            (
                "The day I have spent 6 hours on a recruitment "
                "task and almost got the job"
            ),
        ],
    }

    def get_random_loan_dates(self) -> dict:
        loan_date = now() - timedelta(days=random.randint(1, 90))  # noqa: S311
        due_date = loan_date + timedelta(days=14)
        if due_date < now():
            return_date = due_date - timedelta(days=random.randint(1, 12))  # noqa: S311
        else:
            return_date = None
        return {
            "loan_date": loan_date,
            "due_date": due_date,
            "return_date": return_date,
        }

    def handle(self, *args, **options):
        publishers = PublisherFactory.create_batch(8)
        for author_name, book_titles in self.books_data.items():
            author = AuthorFactory(full_name=author_name)
            for book_title in book_titles:
                book = BookFactory(title=book_title, author=author)
                for _i in range(random.randint(1, 4)):  # noqa: S311
                    edition = BookEditionFactory(
                        book=book,
                        publisher=random.choice(publishers),  # noqa: S311
                    )
                    for _j in range(random.randint(2, 6)):  # noqa: S311
                        is_borrowed = random.randint(0, 5) == 0  # noqa: S311
                        book_copy = BookCopyFactory(
                            book_edition=edition,
                            condition=random.choice(BookCondition.values),  # noqa: S311
                            is_available=not is_borrowed,
                        )
                        if is_borrowed:
                            BookLoanFactory(
                                book_copy=book_copy,
                                **self.get_random_loan_dates(),
                            )
