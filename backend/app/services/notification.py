from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client as TwilioClient
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """Abstract base class for notification services"""

    @abstractmethod
    def send(self, recipient: str, subject: str, content: str, **kwargs) -> bool:
        """Send a notification"""
        pass


class EmailService(NotificationService):
    """Email notification service using SendGrid"""

    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME

    def send(
        self,
        recipient: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Send an email"""
        try:
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=recipient,
                subject=subject,
                plain_text_content=content,
                html_content=html_content or content
            )

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send email to {recipient}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {str(e)}")
            return False

    def send_template(
        self,
        recipient: str,
        template_id: str,
        template_data: Dict[str, Any]
    ) -> bool:
        """Send an email using a template"""
        try:
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=recipient
            )
            message.template_id = template_id
            message.dynamic_template_data = template_data

            response = self.client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Template email sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send template email to {recipient}")
                return False

        except Exception as e:
            logger.error(f"Error sending template email to {recipient}: {str(e)}")
            return False


class SMSService(NotificationService):
    """SMS notification service using Twilio"""

    def __init__(self):
        self.client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = settings.TWILIO_PHONE_NUMBER

    def send(self, recipient: str, subject: str, content: str, **kwargs) -> bool:
        """Send an SMS"""
        try:
            message = self.client.messages.create(
                body=content,
                from_=self.from_number,
                to=recipient
            )

            if message.sid:
                logger.info(f"SMS sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send SMS to {recipient}")
                return False

        except Exception as e:
            logger.error(f"Error sending SMS to {recipient}: {str(e)}")
            return False


class PushNotificationService(NotificationService):
    """Push notification service using Firebase Cloud Messaging"""

    def __init__(self):
        # Initialize Firebase Admin SDK
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")

    def send(
        self,
        recipient: str,  # FCM token
        subject: str,
        content: str,
        data: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> bool:
        """Send a push notification"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=subject,
                    body=content
                ),
                data=data or {},
                token=recipient
            )

            response = messaging.send(message)

            if response:
                logger.info(f"Push notification sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send push notification to {recipient}")
                return False

        except Exception as e:
            logger.error(f"Error sending push notification to {recipient}: {str(e)}")
            return False

    def send_multicast(
        self,
        tokens: List[str],
        subject: str,
        content: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, int]:
        """Send push notification to multiple devices"""
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=subject,
                    body=content
                ),
                data=data or {},
                tokens=tokens
            )

            response = messaging.send_multicast(message)

            logger.info(
                f"Push notifications sent: {response.success_count} successful, "
                f"{response.failure_count} failed"
            )

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count
            }

        except Exception as e:
            logger.error(f"Error sending multicast push notification: {str(e)}")
            return {"success_count": 0, "failure_count": len(tokens)}


class WhatsAppService(NotificationService):
    """WhatsApp notification service using Twilio"""

    def __init__(self):
        self.client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        self.from_number = f"whatsapp:{settings.TWILIO_PHONE_NUMBER}"

    def send(self, recipient: str, subject: str, content: str, **kwargs) -> bool:
        """Send a WhatsApp message"""
        try:
            # Ensure recipient has whatsapp: prefix
            if not recipient.startswith("whatsapp:"):
                recipient = f"whatsapp:{recipient}"

            message = self.client.messages.create(
                body=content,
                from_=self.from_number,
                to=recipient
            )

            if message.sid:
                logger.info(f"WhatsApp message sent successfully to {recipient}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message to {recipient}")
                return False

        except Exception as e:
            logger.error(f"Error sending WhatsApp message to {recipient}: {str(e)}")
            return False


class NotificationManager:
    """Manager class to handle all notification types"""

    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
        self.whatsapp_service = WhatsAppService()

    def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> bool:
        """Send an email notification"""
        return self.email_service.send(recipient, subject, content, html_content=html_content)

    def send_sms(self, recipient: str, content: str) -> bool:
        """Send an SMS notification"""
        return self.sms_service.send(recipient, "", content)

    def send_push(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """Send a push notification"""
        return self.push_service.send(token, title, body, data=data)

    def send_push_multicast(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, int]:
        """Send push notification to multiple devices"""
        return self.push_service.send_multicast(tokens, title, body, data=data)

    def send_whatsapp(self, recipient: str, content: str) -> bool:
        """Send a WhatsApp message"""
        return self.whatsapp_service.send(recipient, "", content)

    def send_all(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        fcm_token: Optional[str] = None,
        subject: str = "",
        content: str = "",
        html_content: Optional[str] = None
    ) -> Dict[str, bool]:
        """Send notification via all available channels"""
        results = {}

        if email:
            results["email"] = self.send_email(email, subject, content, html_content)

        if phone:
            results["sms"] = self.send_sms(phone, content)

        if fcm_token:
            results["push"] = self.send_push(fcm_token, subject, content)

        return results
