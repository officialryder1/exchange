from bitcoinlib.wallets import Wallet, WalletError

def create_wallet(user, currency):
    
    try:
        wallet = Wallet.create(f"{user.email}-{currency}")
        return {
            'public_key': wallet.get_key().address,
            'private_key': wallet.get_key().wif
        }
    
    except WalletError as e:
        wallet = Wallet(f"{user.email}-{currency}")
        return {
            'public_key': wallet.get_key().address,
            'private_key': wallet.get_key().wif
        }