from django.urls import path, include
from .views import CryptoViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', CryptoViewSet)

urlpatterns = [
    path('', include(router.urls))
]