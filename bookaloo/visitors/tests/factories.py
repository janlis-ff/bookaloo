from factory import Faker
from factory import Sequence
from factory.django import DjangoModelFactory

from bookaloo.visitors.models import Visitor


class VisitorFactory(DjangoModelFactory):
    identifier = Sequence(lambda n: str(n).zfill(6))
    full_name = Faker("name")
    email = Faker("email")
    phone_number = Sequence(lambda n: f"+48{n:09}")
    is_active = True

    class Meta:
        model = Visitor
