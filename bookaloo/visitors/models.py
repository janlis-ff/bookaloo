from django.db import models


class Visitor(models.Model):
    identifier = models.CharField(
        max_length=6,
        unique=True,
    )
    full_name = models.CharField(max_length=320)
    email = models.EmailField(max_length=320)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        default="",
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name} #{self.identifier}"
