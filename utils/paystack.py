import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

PAYSTACK_URL = "https://api.paystack.co/transaction/initialize"
VERIFY_URL = "https://api.paystack.co/transaction/verify/"


# ==========================================
# INITIALIZE PAYMENT
# ==========================================

def initialize_payment(email, amount):

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount * 100,      # Kobo
        "currency": "NGN",
        "callback_url": "http://127.0.0.1:5000/verify-payment"
    }

    print("=" * 50)
    print("INITIALIZING PAYSTACK")
    print("EMAIL:", email)
    print("AMOUNT:", amount)
    print("=" * 50)

    response = requests.post(
        PAYSTACK_URL,
        headers=headers,
        json=data,
        timeout=30
    )

    print("STATUS:", response.status_code)
    print("BODY:")
    print(response.text)

    return response.json()


# ==========================================
# VERIFY PAYMENT
# ==========================================

def verify_payment(reference):

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(
        VERIFY_URL + reference,
        headers=headers,
        timeout=30
    )

    return response.json()