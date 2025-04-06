from django.conf.urls import include
from django.urls import re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from ipho_exam import views_api
from ipho_exam.permissions import HasValidApiKeyOrAdmin

router = DefaultRouter()
router.register(r"documents", views_api.DocumentViewSet)

app_name = "api-exam"
urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(
        r"^api-schema/",
        SpectacularAPIView.as_view(
            permission_classes=[
                HasValidApiKeyOrAdmin,
            ],
        ),
        name="schema-api",
    ),
    re_path(
        r"^schema",
        SpectacularSwaggerView.as_view(url_name="api-exam:schema-api"),
        name="schema",
    ),
    # re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
