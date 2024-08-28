from factory import Faker, PostGenerationMethodCall
from factory.django import DjangoModelFactory

from main.models.user import User
from .base import ImageFileProvider


Faker.add_provider(ImageFileProvider)


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    username = Faker("user_name")
    password = PostGenerationMethodCall("set_password", "password")
    avatar_picture = Faker("image_file", fmt="jpeg")

    class Meta:
        model = User
