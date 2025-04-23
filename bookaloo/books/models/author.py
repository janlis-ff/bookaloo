from django.db import models


class Author(models.Model):
    full_name = models.CharField(max_length=480)
    birth_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(
        null=False,
        blank=True,
        default="",
    )

    def __str__(self):
        return self.full_name
