from django.shortcuts import render
from .models import User
from .serializer import UserSerializer, LoginSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, api_view
from rest_framework.views import APIView
from django.db import transaction
from django.contrib.auth import authenticate
import logging
from .mail import send_mail
import random

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .auths import decode_access_token
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def register(self, request):
        logger.info("Registering new User...")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during user registration: {e}")
                return Response({"error": "Something went wrong during registration"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning("Invalid registration data provided.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer
        .errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token is required!"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)

            # Get KYC status
            kyc_status = "Not Submitted"
            if hasattr(user, 'kyc'):
                kyc_status = user.kyc.verification_status

            return Response({
                "user_id": user.id,
                "email": user.email,
                'kyc_status': kyc_status
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class SendMailView(APIView):
#     def post(self, request):
#         token = random.randint(100000, 999999)
#         subject = "Your Verification Code"
#         message = f" Your verification code is {token}"
#         recipient_list = request.data.get('email')

#         if not subject or not message or not recipient_list:
#             return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             send_mail(subject, message, recipient_list)
#             return Response({"success": "Email sent successfully"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
