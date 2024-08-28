from http import HTTPStatus
from typing import OrderedDict

from django.forms import model_to_dict

from main.tests.base import TestViewSetBase, merge
from main.models import Task


class TestUserTasksViewSet(TestViewSetBase):
    basename = "user_tasks"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.task = cls.create_task()

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {
            **attributes,
            "id": entity["id"],
            "deadline": None,
            "priority": None,
        }

    def test_list(self) -> None:
        task1 = self.create_task({"executor": self.user})
        self.create_task()
        
        tasks = self.list(args=[self.user.id])

        assert self.ids(tasks) == [task1.id]

    def test_retrieve_foreign_task(self) -> None:
        task = self.create_task()

        response = self.request_retrieve(args=[self.user.id, task.id])

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_retrieve(self) -> None:
        created_task = self.create_task({"executor": self.user})

        retrieved_task = self.retrieve(args=[self.user.id, created_task.id])

        assert created_task.id == retrieved_task["id"]
