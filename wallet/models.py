from django.db import models

from main.models import User
from crypto.models import Crypto

class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crypto_user")
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    public_key = models.CharField(max_length=255, unique=True, blank=True, null=True)
    private_key = models.CharField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        unique_together = (
            "user",
            "crypto"
        )

    def __str__(self):
        return f"{self.user.email} - {self.crypto.name} Wallet"

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE,  related_name='sent_transactions')
    recipient_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='received_transactions', null=True, blank=True)
    txid = models.CharField(max_length=255, unique=True, blank=True, null=True) # Transaction ID
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    transaction_type = models.CharField(max_length=10, choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer')])
    status = models.CharField(max_length=10, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} {self.wallet.crypto}"