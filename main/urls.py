from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import UserViewSet, LoginView, ChargeWalletView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Create a router for registration
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')


# The API UrLS are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('token/', LoginView.as_view(), name='token_obtain_pair'),
    path('deposit/',ChargeWalletView.as_view(), name="deposit_wallet")
]