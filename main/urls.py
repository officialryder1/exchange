from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import UserViewSet, LoginView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Create a router for registration
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Ensure this is a tuple or list
)

# The API UrLS are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('token/', LoginView.as_view(), name='token_obtain_pair'),

    # OpenAi
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]