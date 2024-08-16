from http import HTTPStatus

from django.urls import reverse

from main.models import User
from .base import TestViewSetBase, merge


class TestUserViewSet(TestViewSetBase):
    basename = "users"
    user: User
    user_attributes = {
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

    def create_user(self, attributes: dict = None) -> dict:
        user_attributes = merge(self.user_attributes, attributes)
        return self.create(user_attributes)

    def test_create(self):
        user = self.create_user()

        expected_response = self.expected_details(user, self.user_attributes)
        assert user == expected_response

    def test_list(self) -> None:
        user1 = self.create_user({"username": "jackbatland"})
        user2 = self.create_user({"username": "janicegriffin"})

        response = self.list()

        self.assert_user_ids(expected=[user1, user2]) 
    
    def test_retrieve(self) -> None:
        self.create_user({"username": "killianmurphy"})
        user2 = self.create_user({"username": "williamfurchtner"})

        response = self.retrieve(user2["id"])

        assert response == user2

    def test_update(self) -> None:
        user = self.create_user({"username": "annabolein"})

        updated_user = self.update(user["id"], self.user_attributes)

        expected_result = self.expected_details(user, self.user_attributes)
        assert updated_user == expected_result

    def test_partial_update(self) -> None:
        user = self.create_user({"username": "ryanjohnson"})

        updated_user = self.partial_update(user["id"], self.user_attributes)

        expected_result = self.expected_details(user, self.user_attributes)
        assert updated_user == expected_result

    def test_delete(self) -> None:
        user1 = self.create_user()
        user2 = self.create_user({"username": "hugostieglitz"})
        
        self.delete(user1)

        self.assert_user_ids(expected=[user2]) 

    def test_user_is_authenticated(self) -> None:
        url = reverse(f"{self.basename}-list")

        response = self.client.get(url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_filter_username(self) -> None:
        new_user = self.create_user({"username": "johannes"})

        self.assert_list_ids(query={"username": "Johan"}, expected=[new_user])
        self.assert_list_ids(query={"username": "jon"}, expected=[])
