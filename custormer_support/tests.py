from django.test import TestCase
from django.utils.timezone import now
from unittest.mock import patch
from main.models import User
from .models import ChatSession, Message

class ChatSupportTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@example.com", password="password123")
        self.chat_session = ChatSession.objects.create(user=self.user)

    def test_chat_session_creation(self):
        """Test that a ChatSession is created successfully."""
        self.assertEqual(self.chat_session.user, self.user)
        self.assertTrue(self.chat_session.is_active)
        self.assertLessEqual(self.chat_session.created_at, now())

    def test_chat_session_string_representation(self):
        """Test the string representation of a ChatSession."""
        expected_str = f"{self.user.email} created a session at {self.chat_session.created_at}"
        self.assertEqual(str(self.chat_session), expected_str)

    def test_message_creation(self):
        """Test that a Message is created successfully."""
        message = Message.objects.create(
            chat_session=self.chat_session,
            sender=self.user,
            message="Hello, how can I help you?",
            is_customer_care=True
        )
        self.assertEqual(message.chat_session, self.chat_session)
        self.assertEqual(message.sender, self.user)
        self.assertEqual(message.message, "Hello, how can I help you?")
        self.assertTrue(message.is_customer_care)
        self.assertLessEqual(message.timestamp, now())

    def test_message_string_representation(self):
        """Test the string representation of a Message."""
        message = Message.objects.create(
            chat_session=self.chat_session,
            sender=self.user,
            message="Hello!"
        )
        expected_str = f"Message from {self.user} in current session: {self.chat_session.id}"
        self.assertEqual(str(message), expected_str)

    @patch('custormer_support.models.pusher_client.trigger')
    def test_message_triggers_pusher_event(self, mock_pusher_trigger):
        """Test that saving a Message triggers a Pusher event."""
        message = Message.objects.create(
            chat_session=self.chat_session,
            sender=self.user,
            message="Hello, how can I assist you?"
        )
        message.save()

       