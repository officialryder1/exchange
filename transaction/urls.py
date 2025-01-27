from django.urls import path, include   
from .views import TransferView, CalculateFeeView


urlpatterns = [
    path('calculate_fee/', CalculateFeeView.as_view(), name='calculate_fee'),
    path('', TransferView.as_view(), name='transfer'),
]