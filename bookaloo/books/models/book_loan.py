from django.db import models
from django.db.models import Q
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from bookaloo.visitors.models import Visitor


class BookLoan(models.Model):
    """
    Represents a single loan of a book copy to a user.
    """

    visitor = models.ForeignKey(
        to=Visitor,
        on_delete=models.PROTECT,
        related_name="book_loans",
        help_text=_("The visitor who has borrowed the book copy."),
    )

    book_copy = models.ForeignKey(
        to="books.BookCopy",
        on_delete=models.PROTECT,
        related_name="loans",
        help_text=_("The specific copy of the book that has been borrowed."),
    )
    loan_date = models.DateTimeField(
        auto_now_add=True,
        help_text=_("The date and time when the book was borrowed."),
    )
    due_date = models.DateTimeField(
        help_text=_("The date and time when the book is due to be returned."),
    )
    return_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("The date and time when the book was returned."),
        default=None,
    )

    class Meta:
        constraints = [
            # Ensure that a book copy can only be loaned to one visitor at a time
            UniqueConstraint(
                fields=["book_copy"],
                condition=Q(return_date__isnull=True),
                name="unique_active_loan_per_book_copy",
            ),
        ]

    def __str__(self):
        return f"Loan of {self.book_copy} to {self.visitor} on {self.loan_date}"
