from django.db import models
from django.utils.translation import gettext_lazy as _

from bookaloo.books.enums import BookCondition


class BookCopy(models.Model):
    """
    Represents a physical copy of a book.
    This includes details like the condition of
    the book and its availability status.
    """

    identifier = models.CharField(
        max_length=6,
        unique=True,
    )

    book_edition = models.ForeignKey(
        to="books.BookEdition",
        on_delete=models.PROTECT,
        related_name="copies",
    )
    condition = models.CharField(
        max_length=20,
        choices=BookCondition.choices,
        default=BookCondition.VERY_GOOD,
    )

    """
    NOTE: `is_available` is a boolean field for indicating
          whether the book is currently borrowed or not.
          It exists for performance reasons, as it is actually
          derived from the fact whether there are any active
          `BookLoan` objects for this book copy or not.
          It should NOT be used as a source of truth.
    """
    is_available = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_(
            "Indicates whether the specific copy of the book"
            "is currently available for borrowing."
        ),
    )

    def __str__(self):
        return f"{self.book_edition.book.title} - Condition: {self.condition}"
