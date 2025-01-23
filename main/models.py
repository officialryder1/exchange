from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
import random


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

USER_ROLE = (
    ('User', 'user'),
    {'Merchant', 'merchant'},
    ('Admin', 'admin')
)

UUID = random.randint(100000, 999999)
class User(AbstractUser):
    # Add your custom fields if any
    username = None
    email = models.EmailField(unique=True)
    fund_password = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    user_role = models.CharField(max_length=8, choices=USER_ROLE, default='user')
    invitation_code = models.CharField(max_length=255, null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_verify = models.BooleanField(default=False)
    UUID = models.CharField(max_length=6, default=UUID)

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


