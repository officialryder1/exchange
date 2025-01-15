
from django.urls import path

from .views import WalletDetailView, deposit_crypto

urlpatterns = [
    path("", WalletDetailView.as_view(), name="wallet"),
    path("deposit_crypto/", deposit_crypto, name="deposit_crypto")
]
