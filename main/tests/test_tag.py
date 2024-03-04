from http import HTTPStatus

from django.urls import reverse

from main.models import Tag
from .base import TestViewSetBase


class TestTagViewSet(TestViewSetBase):
    basename = "tags"
    tag: Tag
    tag_attributes = {"name": "test tag"}

    @staticmethod
    def expected_details(entity: dict, attributes: dict):
        return {**attributes, "id": entity["id"]}

    def test_create(self):
        tag = self.create(self.tag_attributes)
        expected_response = self.expected_details(tag, self.tag_attributes)
        assert tag == expected_response

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
