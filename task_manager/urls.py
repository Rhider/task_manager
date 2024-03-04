from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)

from main.admin import task_manager_admin_site
from main.views import TagViewSet, TaskViewSet, UserViewSet


router = routers.SimpleRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"tasks", TaskViewSet, basename="tasks")


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("admin/", task_manager_admin_site.urls),
    path("api/", include(router.urls)),
]
