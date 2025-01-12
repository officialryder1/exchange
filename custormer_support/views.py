from .models import ChatSession, Message
from rest_framework import status
from rest_framework.response import Response

from rest_framework.decorators import action, api_view
from rest_framework.views import APIView



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