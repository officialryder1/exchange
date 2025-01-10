from django.shortcuts import render
from .models import User, KYC, ChatSession, Message
from .serializer import UserSerializer, LoginSerializer, KYCSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db import transaction
from django.contrib.auth import authenticate
import logging
from .mail import send_mail
import random

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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