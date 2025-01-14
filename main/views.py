from .models import User
from .serializer import UserSerializer, LoginSerializer, VerificationSerializer
from .auths import decode_access_token

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
                return Response({"error": "Something went wrong during registration"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.warning("Invalid registration data provided.")
        return Response({'message': serializer
        .errors}, status=status.HTTP_400_BAD_REQUEST)

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