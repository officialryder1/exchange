from .models import User
from .serializer import UserSerializer, LoginSerializer, VerificationSerializer
from .auths import decode_access_token
from django.conf import settings

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.exceptions import ValidationError

from rest_framework import viewsets, status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import AccessToken

from django.db import transaction
import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema



logger = logging.getLogger(__name__)

class CustomRateThrottle(UserRateThrottle):
    rate = '20/minute' #5 requests per minute

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    throttle_classes = [CustomRateThrottle]

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
                return Response({"message": "Something went wrong during registration"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning("Invalid registration data provided.")
        return Response({'message': serializer
        .errors}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path="google-login")
    @transaction.atomic
    def google_login(self, request):
        """
        Handles login or registration using Google OAuth.
        Expects an access_token from the frontend.
        """
        access_token = request.data.get("access_token")

        if not access_token:
            return Response({"error": "Access token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token using Google's libraries
            idinfo = id_token.verify_oauth2_token(
                access_token,
                google_requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )

            # Extract user info
            email = idinfo.get("email")
            full_name = idinfo.get("name")

            if not email:
                return Response({"error": "Email not found in Google token"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user already exists
            user, created = User.objects.get_or_create(
                email=email,
                
                defaults={
                    "is_active": True,  # Mark the user as active
                    "is_verify": True
                }
            )


            if not created and not user.is_verify:
                # If the user exists but their email isn't verified, mark it as verified
                user.is_verify = True
                user.save()

            # Issue tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_new_user': created  # Frontend can use this to show a welcome message for new users
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in Google login: {e}")
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyUserView(generics.CreateAPIView):
    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Email verified successfully"})


class LoginView(APIView):

    throttle_classes = [CustomRateThrottle]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'message': serializer
        .errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"message": "Token is required!"}, status=status.HTTP_400_BAD_REQUEST)
        
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
                'is_verify': user.is_verify,
                'kyc_status': kyc_status,
                'wallet_balance': user.wallet_balance,
                'uuid': user.UUID
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from decimal import Decimal


# Purpose of this function will be for bonus and offer to new users and any other reason
# and can be used to trade only and can't withdraw or used to buy coin
class ChargeWalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        amount = request.data.get('amount')

        if not amount:
            return Response({"error": "Provide an amount to charge"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.wallet_balance += Decimal(amount)
            user.save()
            return Response({'message': f"wallet successfully charged with {amount}"}, status=status.HTTP_200_OK)
        except ValueError:
            return Response({"message": "Please provide a valid amount."}, status=status.HTTP_400_BAD_REQUEST)
        

