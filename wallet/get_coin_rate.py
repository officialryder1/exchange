
def get_conversion_rate(crypto):
    import requests
    try:
        response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd")
        data = response.json()
        return data.get(crypto, {}).get("usd", 0)
    except (requests.RequestException, KeyError):
        return 0  # Return 0 if the API call fails or the data is unavailable
