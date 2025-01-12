from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import KYCViewSet,KYCDocumentVIew
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Create a router for registration
router = DefaultRouter()
router.register(r'kyc', KYCViewSet)

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Your API",
#         default_version='v1',
#         description="API documentation",
#         terms_of_service="https://www.example.com/terms/",
#         contact=openapi.Contact(email="contact@example.com"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),  # Ensure this is a tuple or list
# )

# The API UrLS are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),

    # KYC Document upload
    path('upload_document/', KYCDocumentVIew.as_view(), name="upload_documents"),

]