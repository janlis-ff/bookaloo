from django.db import models


class BookEdition(models.Model):
    """
    Represents a specific edition of a book.
    This includes details like the publisher, publication date, and ISBN.
    """

    book = models.ForeignKey(
        to="books.Book",
        on_delete=models.PROTECT,
        related_name="editions",
    )
    publisher = models.CharField(max_length=255)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return f"{self.book.title} - ISBN {self.isbn}"
