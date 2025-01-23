from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import KYCViewSet,KYCDocumentView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Create a router for registration
router = DefaultRouter()
router.register(r'', KYCViewSet)


urlpatterns = [
    # KYC Document upload
    path('upload_document/', KYCDocumentView.as_view(), name="upload_document"),
    
    path('', include(router.urls)),


]