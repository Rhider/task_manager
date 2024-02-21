from django.db import models

from .user import User
from .tag import Tag


class Task(models.Model):
    class State(models.TextChoices):
        NEW = "new_task"
        IN_DEV = "in_development"
        IN_QA = "in_qa"
        IN_CR = "in_code_review"
        FOR_RELEASE = "ready_for_release"
        RELEASED = "released"
        ARCHIVED = "archived"

    name = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="tasks_by")
    executor = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="tasks_to_do"
    )
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(null=True)
    state = models.CharField(max_length=255, default=State.NEW, choices=State.choices)
    priority = models.PositiveIntegerField()
    tags = models.ManyToManyField(Tag)
