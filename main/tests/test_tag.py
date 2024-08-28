from http import HTTPStatus

from django.urls import reverse

from main.models import Tag
from .base import TestViewSetBase, merge


class TestTagViewSet(TestViewSetBase):
    basename = "tags"
    tag: Tag
    tag_attributes = {"name": "test tag"}

    @staticmethod
    def expected_details(entity: dict, attributes: dict) -> dict:
        return {**attributes, "id": entity["id"]}

    def create_tag(self, data: dict = None) -> dict:
        attributes = merge(self.tag_attributes, data)
        return self.create(attributes)
    
    def test_create(self) -> None:
        tag = self.create_tag()
        
        expected_response = self.expected_details(tag, self.tag_attributes)
        assert tag == expected_response
    
    def test_list(self) -> None:
        tag1 = self.create_tag({"name": "first tag"})
        tag2 = self.create_tag({"name": "second tag"})
        tag3 = self.create_tag({"name": "third tag"})

        self.assert_list_ids(expected=[tag1, tag2, tag3])        
    
    def test_retrieve(self) -> None:
        self.create_tag({"name": "first tag"})
        tag2 = self.create_tag({"name": "second tag"})

        response = self.retrieve(tag2["id"])

        assert response == tag2

    def test_update(self) -> None:
        tag = self.create_tag({"name": "new tag"})

        updated_tag = self.update(tag["id"], self.tag_attributes)

        expected_result = self.expected_details(tag, self.tag_attributes)
        assert updated_tag == expected_result

    def test_partial_update(self) -> None:
        tag = self.create_tag({"name": "another tag"})

        updated_tag = self.partial_update(tag["id"], self.tag_attributes)

        expected_result = self.expected_details(tag, self.tag_attributes)
        assert updated_tag == expected_result
    
    def test_delete(self) -> None:
        tag1 = self.create_tag()
        tag2 = self.create_tag({"name": "second tag"})
        
        self.delete(tag1["id"])

        self.assert_list_ids(expected=[tag2])        

    def test_user_is_authenticated(self) -> None:
        url = reverse(f"{self.basename}-list")
        
        response = self.client.get(url)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
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
