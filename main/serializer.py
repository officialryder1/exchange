from rest_framework import serializers
from .models import User, KYC, KYCDocument
import random
from django.core.mail import send_mail
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from django.contrib.auth import authenticate


# Authentications
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'fund_password', 'verification_code', 'invitation_code']
        extra_kwargs = {
            'password': { 'write_only': True},
            'fund_password': {'write_only': True}
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
            try:
                send_mail(
                    'Your Verification Code',
                    f"Your verification code is {user.verification_code}",
                    'victor@mail.com',
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # If sending email fails, raise an exception to trigger rollback
                transaction.set_rollback(True)
                raise serializers.ValidationError({'email': 'Failed to send verification email.'})

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


class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = ['full_name', 'date_of_birth', 'address', 'identification_number', 
                  'identification_type', 'verification_status']
    
    def validate_identification_number(self, value):
        # Check if the value is a valid 10 digit number
        if not re.match(r'^\d{10}$', value):
            raise ValidationError('The identification number must be exactly 10 digits long and numeric.')
        
        # Additional custom checks (example: check digit validation)
        # This is just an example of a simple rule; implement a real check later
        check_digit = int(value[-1]) #Assuming the last digit is a check digit
        sum_digits = sum(int(digit) for digit in value[:-1])

        # A simple rule for validation (replace later with a legit logit)
        if(sum_digits % 10) != check_digit:
            raise ValidationError("The digit is invalid")
        
        # if it passes the check, return the value
        return value

class KYCDocumentSerializer(serializers.ModelSerializer):
    id_document = serializers.FileField()
    
    class Meta:
        model = KYCDocument
        fields = ['id_document']