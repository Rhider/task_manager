from unittest.mock import patch, MagicMock

from django.core import mail
from django.template.loader import render_to_string
from django.test import override_settings

from main.models import Task
from task_manager.tasks import send_assign_notification
from main.tests.base import TestViewSetBase, merge

from .factories import UserFactory


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestSendEmail(TestViewSetBase):
    basename = "tasks"
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
    def create_user():
        return UserFactory.create()
    
    def create_task(self, attributes: dict = None) -> dict:
        task_attributes = merge(self.task_attributes, attributes)
        return self.create(task_attributes)
    
    @patch.object(mail, "send_mail")
    def test_send_assign_notification(self, fake_sender: MagicMock) -> None:
        assignee = self.create_user()
        task = self.create_task({"executor": assignee.id})

        send_assign_notification.delay(task["id"])

        fake_sender.assert_called_once_with(
            subject="You've assigned a task.",
            message="",
            from_email=None,
            recipient_list=[assignee.email],
            html_message=render_to_string(
                "emails/notification.html",
                context={"task": Task.objects.get(pk=task["id"])},
            ),
        )
