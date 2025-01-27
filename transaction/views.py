from django.shortcuts import render
from main.models import User
from wallet.models import Wallet, Transaction

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from wallet.serializer import WalletSerializer, TransactionSerializer
from decimal import Decimal
import random

def generate_txid():
    return random.randint(100000000, 999999999)

class TransferView(APIView):
    def post(self, request):
        sender = request.user
        receiver_identifier = request.data.get("recipient")
        currency = request.data.get("currency")
        amount = request.data.get("amount")

        # validate sender wallet
        try:
            sender_wallet = Wallet.objects.get(user=sender, crypto__symbol=currency)
        except Wallet.DoesNotExist:
            return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # validate receiver wallet
        try:
            receiver = User.objects.get(email=receiver_identifier)
            receiver_wallet = Wallet.objects.get(user=receiver, crypto__symbol=currency)
        except (User.DoesNotExist, Wallet.DoesNotExist):
            return Response({"message": "Receiver wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate transaction fee
        fee_percentage = Decimal("0.01")
        fee = int(amount) * fee_percentage

        # validate sender balance including fee
        total_deduction = int(amount) + fee
        if sender_wallet.balance < total_deduction:
            return Response({"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        
        # perform transaction
        sender_wallet.balance -= total_deduction
        receiver_wallet.balance += int(amount)

        # credit transaction fee to admin wallet
        exchange_wallet = Wallet.objects.get(user__email='admin@mail.com', crypto__symbol=currency)

        exchange_wallet.balance += fee

        sender_wallet.save()
        receiver_wallet.save()
        exchange_wallet.save()

        # Record the transaction
        Transaction.objects.create(
            wallet=sender_wallet,
            recipient_wallet=receiver_wallet,
            txid=generate_txid(),  # Generate a unique transaction ID
            amount=amount,
            fee=fee,
            transaction_type='transfer',
            status='Completed'
        )

        return Response({'message': 'Transfer successful', 'fee': str(fee)}, status=status.HTTP_200_OK)
    

class CalculateFeeView(APIView):
    def post(self, request):
        currency = request.data.get("currency")
        amount = request.data.get("amount")

        fee_percentage = Decimal("0.01")
        fee = int(amount) * fee_percentage

        return Response({'fee': str(fee)}, status=status.HTTP_200_OK)