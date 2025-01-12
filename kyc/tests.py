from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import KYC, KYCDocument

User = get_user_model()

class KYCTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@gmail.com",
            password="password123"
        )

        # Create initial KYC data
        self.kyc_data = {
            'full_name': 'Test User',
            'date_of_birth': '1990-01-01',
            'address': '123 Test Street',
            'identification_number': '1234567890',
            'identification_type': 'Passport',
        }

        # Create a KYC record
        self.kyc = KYC.objects.create(user=self.user, **self.kyc_data)

    def test_kyc_creation(self):
        """Test that a KYC record is created successfully."""
        kyc = KYC.objects.get(user=self.user)
        self.assertEqual(kyc.full_name, self.kyc_data['full_name'])
        self.assertEqual(kyc.verification_status, 'PENDING')

    def test_kyc_update(self):
        """Test updating a KYC record."""
        self.kyc.full_name = 'Updated User'
        self.kyc.save()
        updated_kyc = KYC.objects.get(user=self.user)
        self.assertEqual(updated_kyc.full_name, 'Updated User')

    def test_kyc_verification_status(self):
        """Test updating and retrieving the verification status."""
        self.kyc.verification_status = 'APPROVED'
        self.kyc.save()
        approved_kyc = KYC.objects.get(user=self.user)
        self.assertEqual(approved_kyc.verification_status, 'APPROVED')

    def test_kyc_document_upload(self):
        """Test uploading a document to a KYCDocument."""
        document = KYCDocument.objects.create(
            kyc=self.kyc,
            id_document='default.pdf'
        )

        self.assertEqual(document.kyc, self.kyc)
