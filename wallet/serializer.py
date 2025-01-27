from rest_framework import serializers

from .models import Wallet, Transaction
from .get_coin_rate import get_conversion_rate
import random

class WalletSerializer(serializers.ModelSerializer):
    crypto = serializers.StringRelatedField()
    value = serializers.SerializerMethodField()
    crypto_symbol = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ["id", "crypto", "balance", "public_key", "value", "crypto_symbol"]

    def get_value(self, obj):
        crypto_name = str(obj.crypto).lower()
        conversion_rate = get_conversion_rate(crypto_name)
        return obj.balance * conversion_rate

    def get_crypto_symbol(self, obj):
        return getattr(obj.crypto, "symbol", "N/A")

class TransactionSerializer(serializers.ModelSerializer):
    crypto = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = ["id", "wallet", 'crypto', "txid", "amount", "transaction_type", "status", "created_at"]
    
    # def create(self, validated_data):
    #     validated_data['txid'] = random.randint(100000000, 999999999)
    #     return super().create(validated_data)
    
    def get_crypto(self, obj):
        return obj.wallet.crypto.symbol