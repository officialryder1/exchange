from django.db import models
from main.models import User

class KYC(models.Model):
    user =models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc')
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.TextField()
    identification_number = models.CharField(max_length=50)
    identification_type = models.CharField(max_length=50)
   
    verification_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', null=True, blank=True
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
