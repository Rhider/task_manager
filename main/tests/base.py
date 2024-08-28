import copy
from http import HTTPStatus
from typing import List, Union

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.response import Response

from faker.providers import BaseProvider


from main.models import User, Task, Tag


CURRENT_TIME = "2023-06-24T12:00:00Z"


class ImageFileProvider(BaseProvider):
    def image_file(self, fmt: str = "jpeg") -> SimpleUploadedFile:
        return SimpleUploadedFile(
            self.generator.file_name(extension=fmt),
            self.generator.image(image_format=fmt),
        )


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
    task_attributes = {
        "name": "test task",
        "description": "Some task description",
        "created_at": "2023-06-24T12:00:00Z",
        "updated_at": "2023-06-24T12:00:00Z",
        "state": "new_task",
    }
    tag_attributes = {"name": "test tag"}

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
    def create_task(cls, data: dict = None) -> dict:
        task_attributes = merge({
            **cls.task_attributes,
            "author": cls.admin,
            "executor": cls.admin,
        }, data)
        return Task.objects.create(**task_attributes)

    @classmethod
    def create_tag(cls, data: dict = None) -> dict:
        tag_attributes = merge(cls.tag_attributes, data)
        return Tag.objects.create(**tag_attributes)

    @classmethod
    def detail_url(cls, args: Union[int, str]) -> str:
        if isinstance(args, list):
            return reverse(f"{cls.basename}-detail", args=args)
        else:
            return reverse(f"{cls.basename}-detail", args=[args])

    @classmethod
    def list_url(cls, args: List[Union[str, int]] = None) -> str:
        return reverse(f"{cls.basename}-list", args=args)

    def create(self, data: dict, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.post(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.CREATED, response.content
        return response.data

    def request_create(
        self,
        data: dict,
        args: List[Union[str, int]] = None,
        format_type: str = None,
    ) -> Response:
        self.client.force_login(self.user)
        return self.client.post(self.list_url(args), data=data)

    def request_create_multipart(self, data: dict, args: List[Union[str, int]] = None) -> Response:
        return self.request_create(data, args, format_type="multipart")

    def list(self, data: dict = None, args: List[Union[str, int]] = None) -> dict:
        self.client.force_login(self.user)
        response = self.client.get(self.list_url(args), data=data)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data

    def request_retrieve(self, args: Union[str, int]) -> Response:
        self.client.force_login(self.user)
        return self.client.get(self.detail_url(args))

    def retrieve(self, args: Union[str, int]) -> dict:
        response = self.request_retrieve(args)
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

    def delete(self, args: Union[int, list]  = None) -> dict:
        self.client.force_login(self.admin)
        response = self.client.delete(self.detail_url(args))
        assert response.status_code == HTTPStatus.NO_CONTENT
        return response.data

    @classmethod
    def ids(cls, items: List[dict]) -> List[int]:
        return [item["id"] for item in items]

    def assert_list_ids(
        self,
        expected: List[dict],
        query: dict = None,
        args: Union[str, int] = None
    ) -> None:
        entities = self.list(query, args)
        assert self.ids(entities) == self.ids(expected)

    def assert_user_ids(self, expected: List[dict], query: dict = None) -> None:
        entities = self.list(query)
        expected_ids = [self.user.id, self.admin.id] + self.ids(expected)
        assert self.ids(entities) == expected_ids

    def request_single_resource(self, data: dict = None) -> Response:
        self.client.force_login(self.user)
        return self.client.get(self.list_url(), data=data)

    def single_resource(self, data: dict = None) -> dict:
        response = self.request_single_resource(data)
        assert response.status_code == HTTPStatus.OK
        return response.data

    def request_patch_single_resource(self, attributes: dict) -> Response:
        self.client.force_login(self.user)
        return self.client.patch(self.list_url(), data=attributes)

    def patch_single_resource(self, attributes: dict) -> dict:
        response = self.request_patch_single_resource(attributes)
        assert response.status_code == HTTPStatus.OK, response.content
        return response.data
