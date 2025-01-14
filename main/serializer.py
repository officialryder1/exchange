from rest_framework import serializers
from .models import User
import random
from django.core.mail import send_mail
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from django.contrib.auth import authenticate
import time
from smtplib import SMTPException

max_retries = 3
# Authentications
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'fund_password', 'invitation_code', 'wallet_balance']
        extra_kwargs = {
            'password': { 'write_only': True},
            'fund_password': {'write_only': True},
            'wallet_balance': {'read_only': True}
        }


    def create(self, validated_data):
        password = validated_data.pop('password')
        fund_password = validated_data.pop('fund_password')
        user = User(**validated_data)
        user.set_password(password)
        user.fund_password = fund_password
        user.verification_code = str(random.randint(100000, 999999))

        # Using transaction to ensure atomicity
        with transaction.atomic():
            user.save()

            # Send Mail
            for attempt in range(max_retries):
                try:
                    send_mail(
                        'Your Verification Code',
                        f"Your verification code is {user.verification_code}",
                        'your_email@gmail.com',
                        [user.email],
                        fail_silently=False,
                    )
                    break  # Exit the loop if email is sent successfully
                except SMTPException as e:
                    print(f"Error sending email: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(5)  # Wait for 5 seconds before retrying
                    else:
                        raise serializers.ValidationError({'email': 'Failed to send verification email after multiple attempts.'})

        return user
        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Both email and password are required.")

        data['user'] = user
        return data


class VerificationSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        token = attrs.get('token')

        try:
            user = User.objects.get(verification_code=token)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token")
        
        attrs['user'] = user
        return attrs
    
    def create(self, instance, validated_data):
        user = validated_data['user']
        user.is_verify = True
        user.verification_code = None
        user.save()
        return user