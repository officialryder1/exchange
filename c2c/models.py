from django.db import models
from main.models import User

class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_trade")
    crypto = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=80, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, default="open")

    def __str__(self):
        return f"{self.user} made a trade for {self.crypto} - {self.status}"
    
