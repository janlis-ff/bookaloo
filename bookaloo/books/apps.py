from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BooksConfig(AppConfig):
    name = "bookaloo.books"
    verbose_name = _("Books")
