"""
Notification Service - Send notifications via email and messaging.

Supports email notifications, SMS, chat integration (Slack, Teams),
with template rendering and delivery tracking.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    EMAIL = "email"
    SMS = "sms"
    CHAT = "chat"  # Slack, Teams
    IN_APP = "in_app"


class NotificationService:
    """
    Sends notifications via various channels.
    
    Supports:
    - Email notifications
    - SMS notifications
    - Chat platform integration (Slack, Teams)
    - In-app notifications
    - Template rendering
    - Delivery tracking
    """
    
    def __init__(self):
        """Initialize notification service."""
        self.notifications: Dict[str, Dict] = {}
        self.templates: Dict[str, str] = {}
        self._register_default_templates()
        logger.info("NotificationService initialized")
    
    def _register_default_templates(self):
        """Register default notification templates."""
        self.templates["form_submitted"] = """
Notification: Form Submitted

Form: {form_name}
Submission ID: {submission_id}
Submitted by: {submitter_name}
Submitted at: {submitted_at}

Action required: Please review and approve the submission.
Link: {approval_link}
"""
        
        self.templates["approval_request"] = """
Notification: Approval Request

Document: {document_name}
Requested by: {requester_name}
Department: {department}
Deadline: {deadline}

Please review and provide your approval.
Link: {approval_link}
"""
        
        self.templates["document_archived"] = """
Notification: Document Archived

Document: {document_name}
Archived by: {actor_name}
Retention period: {retention_period}
Archive location: {location}

The document has been securely archived.
"""
    
    def send_email(
        self,
        recipient: str,
        subject: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict] = None,
        body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Send an email notification.
        
        Args:
            recipient: Email address
            subject: Email subject
            template_name: Name of template to use
            template_data: Data for template rendering
            body: Raw email body (if not using template)
            attachments: List of file paths to attach
            
        Returns:
            Notification ID
        """
        notification_id = str(uuid.uuid4())
        
        # Render template if provided
        if template_name and template_data:
            body = self._render_template(template_name, template_data)
        
        notification = {
            "notification_id": notification_id,
            "type": NotificationType.EMAIL.value,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "attachments": attachments or [],
            "sent_at": datetime.now().isoformat(),
            "status": "sent",
            "retry_count": 0
        }
        
        self.notifications[notification_id] = notification
        
        logger.info(f"Email sent: {notification_id} to {recipient}")
        
        # In production, use email service (SMTP, SendGrid, etc.)
        # import smtplib
        # from email.mime.text import MIMEText
        
        return notification_id
    
    def send_chat_message(
        self,
        channel: str,
        message: str,
        platform: str = "slack",  # 'slack' or 'teams'
        thread_id: Optional[str] = None
    ) -> str:
        """
        Send a chat notification.
        
        Args:
            channel: Channel name or ID
            message: Message text
            platform: Chat platform (slack, teams)
            thread_id: Optional thread ID for replies
            
        Returns:
            Notification ID
        """
        notification_id = str(uuid.uuid4())
        
        notification = {
            "notification_id": notification_id,
            "type": NotificationType.CHAT.value,
            "platform": platform,
            "channel": channel,
            "message": message,
            "thread_id": thread_id,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self.notifications[notification_id] = notification
        
        logger.info(f"Chat message sent: {notification_id} to {channel}")
        
        # In production, use Slack or Teams API
        # from slack_sdk import WebClient
        # or
        # import requests (for Teams webhooks)
        
        return notification_id
    
    def send_sms(
        self,
        phone_number: str,
        message: str
    ) -> str:
        """
        Send an SMS notification.
        
        Args:
            phone_number: Phone number
            message: SMS message text
            
        Returns:
            Notification ID
        """
        notification_id = str(uuid.uuid4())
        
        notification = {
            "notification_id": notification_id,
            "type": NotificationType.SMS.value,
            "phone_number": phone_number,
            "message": message,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self.notifications[notification_id] = notification
        
        logger.info(f"SMS sent: {notification_id} to {phone_number}")
        
        # In production, use SMS service (Twilio, AWS SNS, etc.)
        # from twilio.rest import Client
        
        return notification_id
    
    def send_notification_batch(
        self,
        recipients: List[Dict],
        subject: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict] = None
    ) -> List[str]:
        """
        Send notifications to multiple recipients.
        
        Args:
            recipients: List of dicts with 'email' and 'type' keys
            subject: Notification subject
            template_name: Template to use
            template_data: Template data
            
        Returns:
            List of notification IDs
        """
        notification_ids = []
        
        for recipient in recipients:
            if recipient.get("type") == "email":
                notif_id = self.send_email(
                    recipient=recipient["email"],
                    subject=subject,
                    template_name=template_name,
                    template_data=template_data
                )
                notification_ids.append(notif_id)
        
        logger.info(f"Batch notifications sent: {len(notification_ids)} recipients")
        return notification_ids
    
    def _render_template(
        self,
        template_name: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Render a template with provided data.
        
        Args:
            template_name: Name of the template
            data: Data for substitution
            
        Returns:
            Rendered template
        """
        if template_name not in self.templates:
            logger.warning(f"Template not found: {template_name}")
            return ""
        
        template = self.templates[template_name]
        
        # Simple substitution - in production use Jinja2 or similar
        for key, value in data.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def register_template(self, name: str, template: str) -> None:
        """
        Register a custom notification template.
        
        Args:
            name: Template name
            template: Template string (with {placeholder} markers)
        """
        self.templates[name] = template
        logger.info(f"Template registered: {name}")
    
    def get_notification_status(self, notification_id: str) -> Optional[Dict]:
        """Get the status of a notification."""
        return self.notifications.get(notification_id)
    
    def list_notifications(
        self,
        notification_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        List notifications.
        
        Args:
            notification_type: Filter by type
            limit: Maximum number to return
            
        Returns:
            List of notifications
        """
        results = list(self.notifications.values())
        
        if notification_type:
            results = [n for n in results if n["type"] == notification_type]
        
        return results[-limit:]
