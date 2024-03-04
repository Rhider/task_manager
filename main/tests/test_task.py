from http import HTTPStatus

from freezegun import freeze_time
from django.urls import reverse

from main.models import Tag, Task
from .base import CURRENT_TIME, TestViewSetBase, merge


@freeze_time(CURRENT_TIME)
class TestTaskViewSet(TestViewSetBase):
    basename = "tasks"
    task: Task
    task_attributes: dict

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.task_attributes = {
            "name": "test task",
            "author": cls.user.id,
            "executor": cls.user.id,
            "description": "Some task description",
            "created_at": "2023-06-24T12:00:00Z",
            "updated_at": "2023-06-24T12:00:00Z",
            "state": "new_task",
            "tags": [],
        }

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {
            **attributes,
            "id": entity["id"],
            "deadline": None,
            "priority": None,
        }

    def test_create(self):
        task = self.create(self.task_attributes)
        expected_response = self.expected_details(task, self.task_attributes)
        assert task == expected_response

    def test_user_is_authenticated(self) -> None:
        url = reverse(f"{self.basename}-list")
        response = self.client.get(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_delete_is_allowed(self) -> None:
        self.client.force_login(self.user)
        url = reverse(f"{self.basename}-detail", args=[1])
        response = self.client.delete(url)

        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {
            "detail": "You do not have permission to perform this action."
        }

    def create_task(self, attributes: dict = None) -> dict:
        task_attributes = merge(self.task_attributes, attributes)
        return self.create(task_attributes)

    def test_filter_state(self) -> None:
        self.create_task()
        task = self.create_task({"state": Task.State.IN_DEV})

        self.assert_list_ids(query={"state": "in_development"}, expected=[task])

    def test_filter_tags(self) -> None:
        tag = Tag.objects.create(name="t")
        tag2 = Tag.objects.create(name="z")
        self.create_task()
        task = self.create_task({"tags": [tag.id, tag2.id]})

        self.assert_list_ids(query={"tags": "t"}, expected=[task])
        self.assert_list_ids(query={"tags": "x"}, expected=[])
        self.assert_list_ids(query={"tags": ["t", "z"]}, expected=[task])

    def test_filter_executor(self) -> None:
        task = self.create_task()

        self.assert_list_ids(query={"executor": "Alex"}, expected=[task])
        self.assert_list_ids(query={"executor": "Lisa"}, expected=[])

    def test_filter_author(self) -> None:
        task = self.create_task()

        self.assert_list_ids(query={"author": "Snow"}, expected=[task])
        self.assert_list_ids(query={"author": "Aleks"}, expected=[])
