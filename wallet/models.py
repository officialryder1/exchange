from django.db import models

from main.models import User
from crypto.models import Crypto

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crypto_user")
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = (
            "user",
            "crypto"
        )

    def __str__(self):
        return f"{self.user.email} - {self.crypto.name}"

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')])
    status = models.CharField(max_length=10, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transition: {self.wallet} - status: {self.status}"