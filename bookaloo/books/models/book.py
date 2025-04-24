from django.db import models


class Book(models.Model):
    """
    Represents a single book, as a literary work;
    regardless of its physical or digital copies.
    """

    title = models.CharField(max_length=380)
    author = models.ForeignKey(
        to="books.Author",
        on_delete=models.PROTECT,
        related_name="books",
    )

    def __str__(self):
        return f'"{self.title}" by {self.author}'
