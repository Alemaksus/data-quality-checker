import requests
import os
from pathlib import Path

# API endpoint and headers
url = "https://dbstage1.paywire.com/pwapi/epf/payment_intents"

# Get API token from environment variable (for security)
api_token = os.getenv("PAYWIRE_API_TOKEN")
if not api_token:
    raise ValueError(
        "PAYWIRE_API_TOKEN environment variable is not set. "
        "Please set it before running this script."
    )

headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Request body
body = {
    "amount": "100",
    "currency": "usd",
    "payment_method_types": ["card", "us_bank_account"],
    "receipt_email": "jerry@jones.com",
    "shipping": {
        "carrier": "ups",
        "confirm": True,
        "capture_method": "automatic",
        "phone": "1231231234",
        "tracking_number": "xyz",
        "address": {
            "city": "jubu"
        },
        "metadata": {
            "tax": "value"
        }
    }
}

# Send POST request 10 times and store IDs only
results_file = Path("results.txt")
with open(results_file, "w") as f:
    for i in range(10):
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            if "client_secret" in data:
                f.write(f"Request {i+1} client_secret: {data['client_secret']}\n")
            else:
                f.write(f"Request {i+1}: 'client_secret' not found in response\n")
        except Exception as e:
            f.write(f"Request {i+1} failed: {e}\n")
