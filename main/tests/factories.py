from factory import Faker, PostGenerationMethodCall
from factory.django import DjangoModelFactory

from main.models.user import User


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    password = PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User
