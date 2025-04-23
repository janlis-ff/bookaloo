from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class BookCondition(TextChoices):
    VERY_GOOD = "Very Good", _("Very Good")
    GOOD = "Good", _("Good")
    ACCEPTABLE = "Acceptable", _("Acceptable")
    POOR = "Poor", _("Poor")
