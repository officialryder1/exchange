from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from .pusher import pusher_client

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Add your custom fields if any
    username = None
    email = models.EmailField(unique=True)
    fund_password = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=6)
    invitation_code = models.CharField(max_length=255, null=True, blank=True)

    # Change related_name for groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    # Set email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Username is not required anymore

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class KYC(models.Model):
    user =models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.TextField()
    identification_number = models.CharField(max_length=50)
    identification_type = models.CharField(max_length=50)
   
    verification_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} KYC Status: {self.verification_status}"
    
class KYCDocument(models.Model):
    kyc = models.ForeignKey(KYC, on_delete=models.CASCADE, related_name="document")
    id_document = models.FileField(upload_to="kyc_document", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.kyc.user.email}"

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
    