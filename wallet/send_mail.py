from django.core.mail import send_mail
from django.conf import settings

def send_deposit_notification(user, amount, crypto):
    
    send_mail(
        'Transaction Notification',
        f"Your deposit of {amount} of {crypto} has been added to your balance wallet",
        settings.EMAIL_HOST,
        [user.email],
        fail_silently=False
    )