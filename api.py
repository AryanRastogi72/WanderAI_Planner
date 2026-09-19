import os
import requests

def get_searchapi_key():
    """
    Retrieves the SearchApi key from the environment variables (.env).
    SearchApi is used to scrape Google Flights, Hotels, and Local results.
    """
    return os.environ.get('SEARCHAPI_API_KEY')

def convert_currency(amount, from_currency, to_currency):
    """
    Convert currency using Frankfurter API (a free API that requires no authentication).
    This is useful if the user requests prices in EUR, GBP, etc.
    """
    # If the currencies are the same, no conversion is needed
    if from_currency == to_currency:
        return amount
    
    try:
        # Make a request to the Frankfurter API
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        response = requests.get(url, timeout=5)
        
        # If the API responds successfully, parse the JSON and return the converted amount
        if response.status_code == 200:
            data = response.json()
            if 'rates' in data and to_currency in data['rates']:
                return float(data['rates'][to_currency])
        
        # Fallback to the original amount if conversion fails
        return amount
    except Exception:
        # Catch any network or timeout errors to prevent the app from crashing
        return amount
