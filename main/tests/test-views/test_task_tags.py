from main.models import Task
from main.tests.base import TestViewSetBase


class TestUserTasksViewSet(TestViewSetBase):
    basename = "task_tags"
    
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.task = cls.create_task()
        cls.tag = cls.create_tag()

    @staticmethod
    def expected_details(entity: dict, attributes: dict) -> dict:
        return {**attributes, "id": entity["id"]}

    def test_list(self) -> None:
        tag2 = self.create_tag({"name": "tag2"})
        self.add_tags(self.task, [self.tag.id, tag2.id])

        tags = self.list(args=[self.task.id])
        assert self.ids(tags) == [self.tag.id, tag2.id]

    def add_tags(self, task: dict, tags: list) -> None:
        task_instance = Task.objects.get(pk=self.task.id)
        task_instance.tags.add(*tags)
        task_instance.save()

    def test_create(self) -> None:
        tag = self.create(data=self.tag_attributes, args=[self.task.id])
        
        expected_response = self.expected_details(tag, self.tag_attributes)
        assert tag == expected_response
    
    def test_update(self) -> None:
        new_tag = self.create_tag({"name": "new tag"})
        self.add_tags(self.task, [new_tag.id])

        updated_tag = self.update(data=self.tag_attributes, args=[self.task.id, new_tag.id])
 
        expected_result = self.expected_details({"id": new_tag.id}, self.tag_attributes)
        assert updated_tag == expected_result

    def test_partial_update(self) -> None:
        tag = self.create_tag({"name": "another tag"})
        self.add_tags(self.task, [tag.id])

        updated_tag = self.partial_update([self.task.id, tag.id], self.tag_attributes)

        expected_result = self.expected_details({"id": tag.id}, self.tag_attributes)
        assert updated_tag == expected_result
    
    def test_delete(self) -> None:
        tag2 = self.create_tag({"name": "second tag"})
        self.add_tags(self.task, [self.tag.id, tag2.id])
        
        self.delete([self.task.id, self.tag.id])

        self.assert_list_ids(expected=[{"id": tag2.id}], args=[self.task.id])
