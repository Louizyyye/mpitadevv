import os
import random
import smtplib
from email.mime.text import MIMEText
import requests
from requests.auth import HTTPBasicAuth

def generate_otp(length=6):
    return str(random.randint(10**(length-1), 10**length-1))

def send_otp_email(email, otp):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    sender = os.getenv('SMTP_SENDER', smtp_user)
    subject = 'Your Mpita Medical OTP'
    body = f'Your OTP is: {otp}'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, [email], msg.as_string())

def get_safaricom_access_token():
    consumer_key = os.getenv('SAFARICOM_CONSUMER_KEY')
    consumer_secret = os.getenv('SAFARICOM_CONSUMER_SECRET')
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    response.raise_for_status()
    return response.json()['access_token']

def send_otp_sms(phone, otp):
    token = get_safaricom_access_token()
    url = 'https://sandbox.safaricom.co.ke/mpesa/sms/v1/send'  # Example endpoint, update to real if needed
    shortcode = os.getenv('SAFARICOM_SHORTCODE')
    sender = os.getenv('SAFARICOM_SENDER', 'MpitaMed')
    payload = {
        'to': phone,
        'message': f'Your OTP is: {otp}',
        'from': sender,
        'shortcode': shortcode
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
