from django.urls import include, path, re_path
from rest_framework import permissions, routers
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from main.admin import task_manager_admin_site
from main.views import (
    TagViewSet,
    TaskTagsViewSet,
    TaskViewSet,
    UserTasksViewSet,
    UserViewSet,
    CurrentUserViewSet,
)
from main.services.single_resource import BulkRouter


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = BulkRouter()
users = router.register(r"users", UserViewSet, basename="users")
users.register(
    r"tasks",
    UserTasksViewSet,
    basename="user_tasks",
    parents_query_lookups=["executor_id"],
)
router.register(r"tags", TagViewSet, basename="tags")
tasks = router.register(r"tasks", TaskViewSet, basename="tasks")
tasks.register(
    r"tags",
    TaskTagsViewSet,
    basename="task_tags",
    parents_query_lookups=["task_id"],
)
router.register(r"current-user", CurrentUserViewSet, basename="current_user")


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", task_manager_admin_site.urls),
    path("api/", include(router.urls)),
]
