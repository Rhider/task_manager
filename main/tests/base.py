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
    client: APIClient = None
    basename: str
    user_attributes = {
        "username": "alexsnow",
        "first_name": "Alex",
        "last_name": "Snow",
        "email": "alex@test.com",
    }

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = cls.create_api_user(cls)
        cls.client = APIClient()

    @staticmethod
    def create_api_user(self):
        return User.objects.create(**self.user_attributes)

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

    def list(self, data: dict, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def retrieve(self, args: Union[str, int] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.detail_url(args))
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def update(self, data: dict, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.put(self.detail_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def delete(self, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.delete(self.detail_url(args))
        assert response.status_code == HTTPStatus.NO_CONTENT
        return response.data

    @classmethod
    def ids(cls, items: List[dict]) -> List[int]:
        return [item["id"] for item in items]

    def assert_list_ids(self, expected: List[dict], query: dict = None) -> None:
        entities = self.list(query)
        assert self.ids(entities) == self.ids(expected)
