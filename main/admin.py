from django.contrib import admin
from .models import User, KYC, ChatSession, Message, KYCDocument

admin.site.register(User)
admin.site.register(KYC)
admin.site.register(ChatSession)
admin.site.register(Message)
admin.site.register(KYCDocument)
