from http import HTTPStatus

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Task, User


class TestTask(APITestCase):
    base_name = "tasks"
    client: APIClient
    task: Task
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = User.objects.create_user("user@test.ru", email=None, password=None)
        cls.client = APIClient()
        cls.task = Task.objects.create(
            name="test task",
            author=cls.user,
            executor=cls.user,
            description="Some task description",
        )

    def test_permission(self) -> None:
        self.assert_is_authenticated()
        self.assert_delete_is_allowed()

    def assert_is_authenticated(self) -> None:
        url = reverse(f"{self.base_name}-list")
        response = self.client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def assert_delete_is_allowed(self) -> None:
        self.client.force_login(self.user)
        url = reverse(f"{self.base_name}-detail", args=[1])
        response = self.client.delete(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "You do not have permission to perform this action."
        }
