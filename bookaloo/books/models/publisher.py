from django.db import models


class Publisher(models.Model):
    """
    Represents a publisher of books.
    This includes details like the name and address of the publisher.
    """

    name = models.CharField(max_length=255)
    address = models.TextField(
        null=False,
        blank=True,
        default="",
    )

    def __str__(self):
        return self.name
