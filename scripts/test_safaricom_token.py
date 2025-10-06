import os
from app.utils.otp import get_safaricom_access_token

if __name__ == "__main__":
    # Make sure your .env is loaded or environment variables are set
    token = get_safaricom_access_token()
    print("Safaricom Access Token:", token)
