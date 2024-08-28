from http import HTTPStatus

from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import model_to_dict
from django.urls import reverse

from main.models import User
from main.tests.factories import UserFactory
from .base import TestViewSetBase, merge


class TestUserViewSet(TestViewSetBase):
    basename = "users"
    user: User
    user_attributes: dict

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {
            **entity,
            "id": entity["id"],
            "avatar_picture": entity["avatar_picture"],
        }

    def create_user(self, attributes: dict = None) -> tuple[dict]:
        new_user = UserFactory.build()
        self.user_attributes = model_to_dict(new_user,
            fields = ["username", "first_name", "last_name", "email", "is_staff", "role"],
        )
        new_user_attributes = merge(self.user_attributes, attributes)
        return self.create(new_user_attributes)

    def test_create(self):
        user = self.create_user()

        expected_response = self.expected_details(user, self.user_attributes)
        assert user == expected_response

    def test_list(self) -> None:
        user1  = self.create_user()
        user2 = self.create_user()

        response = self.list()

        self.assert_user_ids(expected=[user1, user2]) 
    
    def test_retrieve(self) -> None:
        self.create_user()
        user2 = self.create_user()

        response = self.retrieve(user2["id"])

        assert response == user2

    def test_update(self) -> None:
        user = self.create_user()

        updated_user = self.update(user["id"], self.user_attributes)

        expected_result = self.expected_details(user, self.user_attributes)
        expected_result["avatar_picture"] = updated_user["avatar_picture"]
        assert updated_user == expected_result

    def test_partial_update(self) -> None:     
        user = self.create_user()

        updated_user = self.partial_update(user["id"], self.user_attributes)

        expected_result = self.expected_details(user, self.user_attributes)
        assert updated_user == expected_result

    def test_delete(self) -> None:
        user1 = self.create_user()
        user2 = self.create_user()
        
        self.delete(user1["id"])

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

    def test_large_avatar(self) -> None:
        user = UserFactory.build(
            avatar_picture=SimpleUploadedFile("large.jpg", b"x" * 2 * 1024 * 1024)
        )
        user_attributes = model_to_dict(user,
            fields = ["username", "first_name", "last_name", "email", "is_staff", "role", "avatar_picture"],
        )
        
        response = self.request_create_multipart(user_attributes)
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"avatar_picture": ["Maximum size 1048576 exceeded."]}

    def test_avatar_bad_extension(self) -> None:
        user = UserFactory.build()
        user_attributes = model_to_dict(user,
            fields = ["username", "first_name", "last_name", "email", "is_staff", "role", "avatar_picture"],
        )
        user_attributes["avatar_picture"].name = "bad_extension.pdf"
        
        response = self.request_create_multipart(user_attributes)
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {
            "avatar_picture": [
                "File extension “pdf” is not allowed. Allowed extensions are: jpeg, jpg, png."
            ]
        }
