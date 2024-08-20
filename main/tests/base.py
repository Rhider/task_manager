import copy
from http import HTTPStatus
from typing import List, Union

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models.user import User


CURRENT_TIME = "2023-06-24T12:00:00Z"


def merge(base: dict, another_values: dict = None) -> dict:
    result = copy.deepcopy(base)
    if another_values:
        result.update(another_values)
    return result


class TestViewSetBase(APITestCase):
    user: User = None
    admin: User = None
    client: APIClient = None
    basename: str
    user_atributes = {
        "username": "alexsnow",
        "first_name": "Alex",
        "last_name": "Snow",
        "email": "alex@test.com",
    }
    admin_attributes = {
        "username": "victorgroom",
        "first_name": "Victor",
        "last_name": "Groom",
        "email": "victor@test.com",
        "role": "admin"
    }

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = cls.create_api_user(cls)
        cls.admin = cls.create_superuser(cls)
        cls.client = APIClient()

    @staticmethod
    def create_api_user(self):
        return User.objects.create(**self.user_atributes)

    @staticmethod
    def create_superuser(self):
        return User.objects.create_superuser(**self.admin_attributes)

    @classmethod
    def detail_url(cls, key: Union[int, str]) -> str:
        return reverse(f"{cls.basename}-detail", args=[key])

    @classmethod
    def list_url(cls, args: List[Union[str, int]] = None) -> str:
        return reverse(f"{cls.basename}-list", args=args)

    def create(self, data: dict, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.post(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.CREATED, response.content
        return response.data

    def list(self, data: dict = None, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def retrieve(self, args: Union[str, int]) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url(args))
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def update(self, args: Union[str, int], data: dict) -> dict:
        self.client.force_login(self.user)
        response = self.client.put(self.detail_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data
    
    def partial_update(self, args: Union[str, int], data: dict) -> dict:
        self.client.force_login(self.user)
        response = self.client.patch(self.detail_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def delete(self, args: dict = None) -> dict:
        self.client.force_login(self.admin)
        response = self.client.delete(self.detail_url(args["id"]))
        assert response.status_code == HTTPStatus.NO_CONTENT
        return response.data

    @classmethod
    def ids(cls, items: List[dict]) -> List[int]:
        return [item["id"] for item in items]

    def assert_list_ids(self, expected: List[dict], query: dict = None) -> None:
        entities = self.list(query)
        assert self.ids(entities) == self.ids(expected)

    def assert_user_ids(self, expected: List[dict], query: dict = None) -> None:
        entities = self.list(query)
        expected_ids = [self.user.id, self.admin.id] + self.ids(expected)
        assert self.ids(entities) == expected_ids
