import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class Config:
    """Central configuration for email, SMS providers, and OTP settings."""

    # Gmail (use App Password with 2FA)
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'mhharshith9@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', '')

    # Twilio (optional; used if provided)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    # AWS SNS (optional; used if provided)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

    # OTP settings
    OTP_LENGTH = int(os.getenv('OTP_LENGTH', '6'))
    OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', '10'))
    MAX_OTP_ATTEMPTS = int(os.getenv('MAX_OTP_ATTEMPTS', '3'))

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Gmail Configuration for OTP Emails
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL', 'mhharshith9@gmail.com')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD', 'Harshith@#123')
    
    # Twilio Configuration for SMS OTP
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Alternative: AWS SNS for SMS
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Firebase Configuration
    FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    
    # OTP Configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_OTP_ATTEMPTS = 3
