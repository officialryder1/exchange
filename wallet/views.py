from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404
from crypto.models import Crypto
from decimal import Decimal

from .models import Wallet
from .models import Wallet, Transaction
from .serializer import WalletSerializer
from .send_mail import send_deposit_notification


class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wallet = Wallet.objects.filter(user=user)
        serializer = WalletSerializer(wallet, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_crypto(request):
    """
    Handle deposit of crypto into user wallet
    """

    user = request.user
    crypto_symbol = request.data.get('crypto_symbol')
    amount = request.data.get('amount')

    # validate input
    if not crypto_symbol or not amount:
        return Response({'error': "Crypto symbol and amount are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get the crypto object
    crypto = get_object_or_404(Crypto, symbol=crypto_symbol)
    wallet, created = Wallet.objects.get_or_create(user=user, crypto=crypto)
    transaction = Transaction.objects.create(wallet=wallet, amount=amount, transaction_type='deposit', status='pending')

    # Simulate the deposit process (e.g., check blockchain for deposit)
    # For example, you might have a service that checks for incoming transactions.
    # This is a simplified example without actual blockchain interaction.
    wallet.balance += Decimal(amount)
    wallet.save()
    user.wallet_balance -= Decimal(amount)
    user.save()
    transaction.status = 'completed'
    transaction.save()

    send_deposit_notification(user, amount, crypto)

    return Response({'message': 'Deposit successful', 'balance': wallet.balance}, status=status.HTTP_200_OK)
