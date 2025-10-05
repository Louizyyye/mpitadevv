# app/daraja_client.py
import os
import base64
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------------
# Environment configuration
# -------------------------------------------------------------------------
DAR_AJA_ENV = os.getenv("DAR_AJA_ENV", "sandbox").lower()
CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")

if DAR_AJA_ENV == "production":
    OAUTH_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    B2C_URL = "https://api.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
else:
    OAUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    B2C_URL = "https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------
def _timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")

def _password(shortcode: str, passkey: str, timestamp: str) -> str:
    raw = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()

def get_access_token() -> str:
    """Retrieve OAuth access token from Daraja."""
    if not CONSUMER_KEY or not CONSUMER_SECRET:
        raise RuntimeError("MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET must be set")

    resp = requests.get(OAUTH_URL, auth=(CONSUMER_KEY, CONSUMER_SECRET), timeout=15)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"No access token in response: {data}")
    return token

# -------------------------------------------------------------------------
# Daraja API Functions
# -------------------------------------------------------------------------
def stk_push(amount: float, phone_number: str, account_reference: str, description: str) -> Dict[str, Any]:
    """Trigger an STK push to a customer phone."""
    if not SHORTCODE or not PASSKEY or not CALLBACK_URL:
        raise RuntimeError("SHORTCODE, PASSKEY and CALLBACK_URL must be configured")

    timestamp = _timestamp()
    password = _password(SHORTCODE, PASSKEY, timestamp)
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": description
    }

    resp = requests.post(STK_PUSH_URL, json=payload, headers=headers, timeout=20)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"ok": False, "status_code": resp.status_code, "body": resp.text}
    return {"ok": True, "status_code": resp.status_code, "body": resp.json()}

def airtime_push(phone_number: str, amount: float, provider: str = "Safaricom") -> Dict[str, Any]:
    """Send Airtime to a customer using B2C endpoint."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "InitiatorName": "testapi",  # Replace with your registered Initiator
        "SecurityCredential": "xxxx",  # Daraja-generated encrypted password
        "CommandID": "SalaryPayment",  # Example command
        "Amount": int(amount),
        "PartyA": SHORTCODE,
        "PartyB": phone_number,
        "Remarks": f"Airtime topup {provider}",
        "QueueTimeOutURL": CALLBACK_URL,
        "ResultURL": CALLBACK_URL,
        "Occasion": "Airtime"
    }

    resp = requests.post(B2C_URL, json=payload, headers=headers, timeout=20)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"ok": False, "status_code": resp.status_code, "body": resp.text}
    return {"ok": True, "status_code": resp.status_code, "body": resp.json()}

def bank_payment(account_number: str, bank_code: str, amount: float, reference: str = "MpitaBank") -> Dict[str, Any]:
    """Send payment to a bank account via B2C API."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "InitiatorName": "testapi",  # Replace with your registered Initiator
        "SecurityCredential": "xxxx",  # Daraja-generated encrypted password
        "CommandID": "BusinessPayment",
        "Amount": int(amount),
        "PartyA": SHORTCODE,
        "PartyB": account_number,
        "BankCode": bank_code,
        "Remarks": reference,
        "QueueTimeOutURL": CALLBACK_URL,
        "ResultURL": CALLBACK_URL
    }

    resp = requests.post(B2C_URL, json=payload, headers=headers, timeout=20)
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        return {"ok": False, "status_code": resp.status_code, "body": resp.text}
    return {"ok": True, "status_code": resp.status_code, "body": resp.json()}
