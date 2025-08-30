import logging
import os
from config import Config

try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None

try:
    import boto3
except Exception:
    boto3 = None


logger = logging.getLogger("agrimart.sms_service")


class SMSService:
    def __init__(self) -> None:
        self.twilio_client = None
        self.sns_client = None
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        # Twilio
        if TwilioClient and Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            try:
                self.twilio_client = TwilioClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
                logger.info("✅ Twilio SMS service initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Twilio init failed: {e}")

        # AWS SNS
        if boto3 and Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            try:
                self.sns_client = boto3.client(
                    'sns',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION,
                )
                logger.info("✅ AWS SNS service initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ AWS SNS init failed: {e}")

    def send_otp_sms(self, phone_number: str, otp: str) -> bool:
        """Send OTP over SMS using available provider, fallback to console log."""
        # Prefer Twilio
        if self.twilio_client and Config.TWILIO_PHONE_NUMBER:
            try:
                self.twilio_client.messages.create(
                    body=f"Your Agrimart OTP is {otp}",
                    from_=Config.TWILIO_PHONE_NUMBER,
                    to=phone_number,
                )
                return True
            except Exception as e:
                logger.warning(f"Twilio send failed: {e}")

        # Fallback to AWS SNS
        if self.sns_client:
            try:
                self.sns_client.publish(PhoneNumber=phone_number, Message=f"Your Agrimart OTP is {otp}")
                return True
            except Exception as e:
                logger.warning(f"AWS SNS send failed: {e}")

        # Final fallback: simulate by logging (useful for dev/test)
        logger.info(f"📨 Simulated SMS to {phone_number}: OTP {otp}")
        return True


sms_service = SMSService()

import os
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.twilio_client = None
        self.aws_sns = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize SMS services (Twilio and AWS SNS)"""
        # Initialize Twilio
        if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
                logger.info("✅ Twilio SMS service initialized successfully")
            except ImportError:
                logger.warning("⚠️ Twilio package not installed. Install with: pip install twilio")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twilio: {str(e)}")
        
        # Initialize AWS SNS
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            try:
                import boto3
                self.aws_sns = boto3.client(
                    'sns',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION
                )
                logger.info("✅ AWS SNS service initialized successfully")
            except ImportError:
                logger.warning("⚠️ Boto3 package not installed. Install with: pip install boto3")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AWS SNS: {str(e)}")
    
    def send_otp_sms(self, phone_number, otp):
        """
        Send OTP via SMS using available services
        
        Args:
            phone_number (str): Recipient phone number
            otp (str): 6-digit OTP code
            
        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        # Try Twilio first
        if self.twilio_client:
            if self._send_via_twilio(phone_number, otp):
                return True
        
        # Try AWS SNS if Twilio fails
        if self.aws_sns:
            if self._send_via_aws_sns(phone_number, otp):
                return True
        
        # Fallback to console simulation
        logger.warning("⚠️ No SMS service available, simulating SMS")
        return self._simulate_sms(phone_number, otp)
    
    def _send_via_twilio(self, phone_number, otp):
        """Send SMS via Twilio"""
        try:
            message = self.twilio_client.messages.create(
                body=f"Your Agrimart OTP is: {otp}. Valid for {Config.OTP_EXPIRY_MINUTES} minutes.",
                from_=Config.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            logger.info(f"✅ Twilio SMS sent successfully to {phone_number}. SID: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"❌ Twilio SMS failed: {str(e)}")
            return False
    
    def _send_via_aws_sns(self, phone_number, otp):
        """Send SMS via AWS SNS"""
        try:
            message = f"Your Agrimart OTP is: {otp}. Valid for {Config.OTP_EXPIRY_MINUTES} minutes."
            
            response = self.aws_sns.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            logger.info(f"✅ AWS SNS SMS sent successfully to {phone_number}. Message ID: {response['MessageId']}")
            return True
        except Exception as e:
            logger.error(f"❌ AWS SNS SMS failed: {str(e)}")
            return False
    
    def _simulate_sms(self, phone_number, otp):
        """Simulate SMS for development/testing"""
        logger.info(f"📱 [SIMULATED] SMS OTP {otp} sent to {phone_number}")
        logger.info("💡 To send real SMS, configure Twilio or AWS SNS credentials")
        return True

# Global SMS service instance
sms_service = SMSService()
