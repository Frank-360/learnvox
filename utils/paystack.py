import os
import requests

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")

BASE_URL = "https://api.paystack.co"


def initialize_payment(email, amount):

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "amount": amount * 100  # Kobo
    }

    response = requests.post(
        f"{BASE_URL}/transaction/initialize",
        json=payload,
        headers=headers
    )

    return response.json()