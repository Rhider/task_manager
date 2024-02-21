from django.urls import path, include
from rest_framework import routers

from main.admin import task_manager_admin_site
from main.views import TagViewSet, TaskViewSet, UserViewSet


router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"tasks", TaskViewSet, basename="tasks")


urlpatterns = [
    path("admin/", task_manager_admin_site.urls),
    path("api/", include(router.urls)),
]
