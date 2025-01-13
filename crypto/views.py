from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle

from .models import Crypto
from .serializer import CryptoSerializer

class CustomRateThrottle(UserRateThrottle):
    rate = '5/minute' #5 requests per minute

class CryptoViewSet(viewsets.ModelViewSet):
    queryset = Crypto.objects.all()
    serializer_class = CryptoSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    throttle_classes = [CustomRateThrottle]

    # def get_permissions(self):
    #     if self.request.method in ["POST", "PUT", "DELETE"]:
    #         self.permission_classes = [permissions.IsAdminUser]
    #     return super().get_permission()
    