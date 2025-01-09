from django.test import TestCase

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import User

class UserRegistrationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')  # Ensure this name matches the URL pattern for the register action

    def test_user_registration_successful(self):
        """
        Test registering a new user successfully.
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'strongpassword123',
            'fund_password': 'fundpass123',
            'verification_code': '123456',
            'invitation_code': 'INVITE123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_registration_missing_fields(self):
        """
        Test registering a user with missing required fields.
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'strongpassword123'
            # Missing other required fields
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        """
        Test registering a user with an invalid email.
        """
        data = {
            'email': 'invalidemail',
            'password': 'strongpassword123',
            'fund_password': 'fundpass123',
            'verification_code': '123456',
            'invitation_code': 'INVITE123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_duplicate_email(self):
        """
        Test registering a user with an email that already exists.
        """
        User.objects.create_user(
            email='testuser@example.com', password='strongpassword123'
        )
        data = {
            'email': 'testuser@example.com',
            'password': 'anotherpassword123',
            'fund_password': 'fundpass123',
            'verification_code': '123456',
            'invitation_code': 'INVITE123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

