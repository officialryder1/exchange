from django.core.mail import send_mail
from django.conf import settings

def send_mail(subject, message, recipient_list):
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST,
        recipient_list,
        fail_silently=False
    )