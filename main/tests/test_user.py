from http import HTTPStatus

from django.urls import reverse

from main.models import User
from .base import TestViewSetBase, merge


class TestUserViewSet(TestViewSetBase):
    basename = "users"
    user: User
    user_atributes = {
        "username": "johnsmith",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@test.com",
        "is_staff": False,
        "role": "developer",
    }

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {**attributes, "id": entity["id"]}

    def test_create(self):
        user = self.create(self.user_atributes)
        expected_response = self.expected_details(user, self.user_atributes)
        assert user == expected_response

    def test_user_is_authenticated(self) -> None:
        url = reverse(f"{self.basename}-list")
        response = self.client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_filter_username(self) -> None:
        new_user = self.create(merge(self.user_attributes, {"username": "johannes"}))
        self.assert_list_ids(query={"username": "Johan"}, expected=[new_user])
        self.assert_list_ids(query={"username": "jon"}, expected=[])
