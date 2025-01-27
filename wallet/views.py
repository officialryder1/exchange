from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404
from crypto.models import Crypto
from decimal import Decimal
from django.db import transaction

from .models import Wallet
from .models import Wallet, Transaction
from .serializer import WalletSerializer, TransactionSerializer
from .send_mail import send_deposit_notification

from .create_wallet import create_wallet

from main.models import User


class TransactionPagination(PageNumberPagination):
    page_size = 5
   

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
    def create_wallet(self, request):
        user = request.user
        crypto_symbol = request.data.get('crypto_symbol')

        if not crypto_symbol:
            return Response({'error': 'Crypto symbol is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        crypto = get_object_or_404(Crypto, symbol=crypto_symbol)

        wallet_address = create_wallet(user, crypto_symbol)

        public = wallet_address['public_key']
        private = wallet_address['private_key']
        wallet = Wallet.objects.create(user=user, crypto=crypto, public_key=public, private_key=private)

        return Response({'message': 'Wallet created successfully', 'public_key': wallet.public_key}, status=status.HTTP_201_CREATED)

      
    

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionPagination

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user).order_by('-created_at')

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

    # send_deposit_notification(user, amount, crypto)

    return Response({'message': 'Deposit successful', 'balance': wallet.balance}, status=status.HTTP_200_OK)
