from rest_framework import serializers
from .models import KYC, KYCDocument
from django.core.exceptions import ValidationError
import re


class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = ['full_name', 'date_of_birth', 'address', 'identification_number', 
                  'identification_type']
    
    def validate_identification_number(self, value):
        # Check if the value is a valid 10 digit number
        if not re.match(r'^\d{11}$', value):
            raise ValidationError('The identification number must be exactly 10 digits long and numeric.')
        
        # Additional custom checks (example: check digit validation)
        # This is just an example of a simple rule; implement a real check later
        check_digit = int(value[-1]) #Assuming the last digit is a check digit
        sum_digits = sum(int(digit) for digit in value[:-1])

        # # A simple rule for validation (replace later with a legit logit)
        # if(sum_digits % 10) != check_digit:
        #     raise ValidationError("The digit is invalid")
        
        # if it passes the check, return the value
        return value

class KYCDocumentSerializer(serializers.ModelSerializer):
    id_document = serializers.FileField()
    
    class Meta:
        model = KYCDocument
        fields = ['id_document']
    
    def create(self, validated_data):
        # Save the file and associate it with a KYC record
        return KYCDocument.objects.create(**validated_data)