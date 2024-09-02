from typing import Any, cast

from django.http import Http404
from django.urls import reverse
import django_filters
from rest_framework import permissions, viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_extensions.mixins import NestedViewSetMixin
from main.services.single_resource import SingleResourceMixin, SingleResourceUpdateMixin
from main.services.async_celery import AsyncJob, JobStatus
from .models import Tag, Task, User
from .serializers import (
    CountdownJobSerializer,
    JobSerializer,
    TagSerializer,
    TaskSerializer,
    UserSerializer,
)


class DeleteAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return bool(request.user and request.user.is_staff)
        return True


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name="username", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ("username",)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("id")
    serializer_class = UserSerializer
    filterset_class = UserFilter


class CurrentUserViewSet(
    SingleResourceMixin, SingleResourceUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = UserSerializer
    queryset = User.objects.order_by("id")

    def get_object(self) -> User:
        return cast(User, self.request.user)


class UserTasksViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = (
        Task.objects.order_by("id")
        .select_related("author", "executor")
        .prefetch_related("tags")
    )
    serializer_class = TaskSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.order_by("id")
    serializer_class = TagSerializer
    permission_classes = (
        DeleteAdminOnly,
        IsAuthenticated,
    )


class TaskTagsViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    
    def get_queryset(self):
        task_id = self.kwargs["parent_lookup_task_id"]
        return Task.objects.get(pk=task_id).tags.all()


class TaskFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(lookup_expr="iexact")
    tags = django_filters.CharFilter(field_name="tags__name", lookup_expr="in")
    executor = django_filters.CharFilter(
        field_name="executor__username",
        lookup_expr="icontains",
    )
    author = django_filters.CharFilter(
        field_name="author__username",
        lookup_expr="icontains",
    )

    class Meta:
        model = Task
        fields = ("state", "tags", "executor", "author")


class TaskViewSet(viewsets.ModelViewSet):
    queryset = (
        Task.objects.select_related("author", "executor")
        .prefetch_related("tags")
        .order_by("id")
    )
    serializer_class = TaskSerializer
    filterset_class = TaskFilter
    permission_classes = (
        DeleteAdminOnly,
        IsAuthenticated,
    )


class CountdownJobViewSet(CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CountdownJobSerializer

    def get_success_headers(self, data: dict) -> dict[str, str]:
        task_id = data["task_id"]
        return {"Location": reverse("jobs-detail", args=[task_id])}


class AsyncJobViewSet(viewsets.GenericViewSet):
    serializer_class = JobSerializer

    def get_object(self) -> AsyncJob:
        lookup_url_kwargs = self.lookup_url_kwarg or self.lookup_field
        task_id = self.kwargs[lookup_url_kwargs]
        job = AsyncJob.from_id(task_id)
        if job.status == JobStatus.UNKNOWN:
            raise Http404()
        return job

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer_data = self.get_serializer(instance).data
        if instance.status == JobStatus.SUCCESS:
            location = self.request.build_absolute_uri(instance.result)
            return Response(
                serializer_data,
                headers={"location": location},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer_data)
