
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet, TransactionViewSet, deposit_crypto

router = DefaultRouter()
router.register(r"wallet", WalletViewSet, basename="wallet")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path('', include(router.urls)),
    path("deposit_crypto/", deposit_crypto, name="deposit_crypto"),
]
