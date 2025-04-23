from django.urls import include
from django.urls import path
from rest_framework.routers import SimpleRouter

from bookaloo.books.views import BookLoanView
from bookaloo.books.views import BookReturnView
from bookaloo.books.viewsets import AuthorViewSet
from bookaloo.books.viewsets import BookCopyViewSet
from bookaloo.books.viewsets import BookEditionViewSet
from bookaloo.books.viewsets import BookViewSet
from bookaloo.books.viewsets import PublisherViewSet

app_name = "books"

authors_router = SimpleRouter()
authors_router.register("authors", AuthorViewSet, basename="authors")

publishers_router = SimpleRouter()
publishers_router.register("publishers", PublisherViewSet, basename="publishers")

books_router = SimpleRouter()
books_router.register(
    "",
    BookViewSet,
    basename="books",
)
books_router.register(
    "<int:book_id>/editions",
    BookEditionViewSet,
    basename="book-editions",
)
books_router.register(
    "<int:book_id>/editions/<int:edition_id>/copies",
    BookCopyViewSet,
    basename="book-edition-copies",
)

urlpatterns = [
    path("", include(authors_router.urls)),
    path("", include(publishers_router.urls)),
    path("", include(books_router.urls)),
    path(
        "loans",
        BookLoanView.as_view(),
        name="book-loans",
    ),
    path(
        "returns",
        BookReturnView.as_view(),
        name="book-returns",
    ),
]
