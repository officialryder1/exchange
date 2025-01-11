from django.shortcuts import render
from .models import User, KYC, ChatSession, Message,KYCDocument
from .serializer import UserSerializer, LoginSerializer, KYCSerializer, KYCDocumentSerializer
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
from .pusher import pusher_client
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


class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff:
            return KYC.objects.all() # Only Admin can see all KYC entries
        return KYC.objects.filter(User=self.request.user) # Regular users see their own KYC entries
    

class KYCDocumentVIew(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_document': openapi.Schema(type=openapi.TYPE_FILE, description='KYC Document'),
            }
        ),
        responses={201: 'Document uploaded successfully', 400: 'Bad Request'}
    )

    def post(self, request):
        kyc = KYC.objects.filter(user=request.user).first()
        if not kyc:
            return Response({"error": "KYC record not found for user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = KYCDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(kyc=kyc)
            return Response({"success": "Document uploaded successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        kyc = KYC.objects.filter(user=request.user).first()
        if not kyc:
            return Response({"error": "KYC record not found for user."}, status=status.HTTP_404_NOT_FOUND)

        document = KYCDocument.objects.filter(kyc=kyc).first()
        if not document:
            return Response({"error": "No document found for this KYC record."}, status=status.HTTP_404_NOT_FOUND)

        serializer = KYCDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateChatSessionView(APIView):
    def post(self, request):
        user = request.user
        chat_session = ChatSession.objects.create(user=user)
        return Response({"chat_session_id": chat_session.id}, status=status.HTTP_201_CREATED)
    

class SendMessageView(APIView):
    def post(self, request, session_id):
        user = request.user
        message_text = request.data.get('message')
        is_customer_care = request.data.get('is_customer_care', False)
        chat_session = ChatSession.objects.get(id=session_id)

        message = Message.objects.create(
            chat_session=chat_session,
            sender = user,
            message=message_text,
            is_customer_care=is_customer_care
        )
        return Response({"message": "message sent successfully"}, status=status.HTTP_200_OK)
    
class GetMessageView(APIView):
    def get(self, request, session_id):
        messages = Message.objects.filter(chat_session_id=session_id)
        return Response(
            {"message": [msg.message for msg in messages]},
            status=status.HTTP_200_OK
        )