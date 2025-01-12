from django.db import models
from .pusher import pusher_client
from main.models import User

# Create your models here.
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} created a session at {self.created_at}"

class Message(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="message")
    sender = models.ForeignKey(User, on_delete=models.Case)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_customer_care = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Trigger Pusher evebt
        pusher_client.trigger(
            f"chat_{self.chat_session.id}",
            'new_message',
            {
                'sender': self.sender.username,
                'message': self.message,
                'timestamp': self.timestamp.isoformat()
            }
        )

    def __str__(self):
        return f"Message from {self.sender} in current session: {self.chat_session.id}"
    