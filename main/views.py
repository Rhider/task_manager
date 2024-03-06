import django_filters
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Tag, Task, User
from .serializers import TagSerializer, TaskSerializer, UserSerializer


class DeleteAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE":
            return bool(request.user and request.user.is_staff)
        return True


class UserFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="username", lookup_expr="icontains")

    class Meta:
        model = User
        fields = ("name",)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by("id")
    serializer_class = UserSerializer
    filterset_class = UserFilter


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.order_by("id")
    serializer_class = TagSerializer
    permission_classes = (
        DeleteAdminOnly,
        IsAuthenticated,
    )


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
