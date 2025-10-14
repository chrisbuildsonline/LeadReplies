#!/usr/bin/env python3
"""
Notification Service for Lead Replier
Handles creating and sending notifications for various events
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging
from typing import Optional, Dict, Any

from database import Database

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.db = Database()
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
    
    def create_notification(self, user_id: int, notification_type: str, title: str, 
                          message: str, data: Optional[Dict[Any, Any]] = None, 
                          priority: str = 'normal') -> Optional[int]:
        """Create a new notification and optionally send email"""
        try:
            # Create the notification in database
            notification_id = self.db.create_notification(
                user_id, notification_type, title, message, data, priority
            )
            
            if notification_id:
                # Check if user wants email notifications for this type
                if self.db.should_send_email_notification(user_id, notification_type):
                    self._send_email_notification(user_id, title, message, data)
                
                logger.info(f"Created notification {notification_id} for user {user_id}")
                return notification_id
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
        
        return None
    
    def notify_new_lead(self, user_id: int, lead_data: Dict[Any, Any]) -> Optional[int]:
        """Notify user about a new lead"""
        title = f"New Lead Found: {lead_data.get('title', 'Untitled')[:50]}..."
        message = f"A new lead has been discovered on {lead_data.get('platform', 'unknown platform')} with an AI score of {lead_data.get('ai_score', 0)}%"
        
        return self.create_notification(
            user_id=user_id,
            notification_type='new_lead',
            title=title,
            message=message,
            data={
                'lead_id': lead_data.get('id'),
                'platform': lead_data.get('platform'),
                'ai_score': lead_data.get('ai_score'),
                'url': lead_data.get('url'),
                'subreddit': lead_data.get('subreddit')
            },
            priority='high' if lead_data.get('ai_score', 0) >= 80 else 'normal'
        )
    
    def notify_reply_posted(self, user_id: int, reply_data: Dict[Any, Any]) -> Optional[int]:
        """Notify user about a posted reply"""
        title = f"Reply Posted Successfully"
        message = f"Your automated reply has been posted to {reply_data.get('platform', 'unknown platform')}"
        
        return self.create_notification(
            user_id=user_id,
            notification_type='reply_posted',
            title=title,
            message=message,
            data={
                'reply_id': reply_data.get('id'),
                'platform': reply_data.get('platform'),
                'lead_title': reply_data.get('lead_title'),
                'platform_reply_id': reply_data.get('platform_reply_id')
            },
            priority='normal'
        )
    
    def notify_ai_suggestion_ready(self, user_id: int, suggestion_data: Dict[Any, Any]) -> Optional[int]:
        """Notify user about an AI reply suggestion"""
        title = f"AI Reply Suggestion Ready"
        message = f"AI has generated a reply suggestion for a lead on {suggestion_data.get('platform', 'unknown platform')}"
        
        return self.create_notification(
            user_id=user_id,
            notification_type='ai_suggestion_ready',
            title=title,
            message=message,
            data={
                'lead_id': suggestion_data.get('lead_id'),
                'platform': suggestion_data.get('platform'),
                'lead_title': suggestion_data.get('lead_title'),
                'suggestion_preview': suggestion_data.get('suggestion', '')[:100] + '...'
            },
            priority='medium'
        )
    
    def notify_account_verification(self, user_id: int, account_data: Dict[Any, Any]) -> Optional[int]:
        """Notify user about account verification status"""
        status = account_data.get('status', 'unknown')
        platform = account_data.get('platform', 'unknown')
        username = account_data.get('username', 'unknown')
        
        if status == 'verified':
            title = f"Account Verified: {platform}"
            message = f"Your {platform} account (@{username}) has been successfully verified and is ready for automation"
            priority = 'normal'
        else:
            title = f"Account Verification Failed: {platform}"
            message = f"Failed to verify your {platform} account (@{username}). Please check your credentials"
            priority = 'high'
        
        return self.create_notification(
            user_id=user_id,
            notification_type='account_verification',
            title=title,
            message=message,
            data=account_data,
            priority=priority
        )
    
    def notify_scraper_status(self, user_id: int, status_data: Dict[Any, Any]) -> Optional[int]:
        """Notify user about scraper status changes"""
        status = status_data.get('status', 'unknown')
        
        if status == 'offline':
            title = "Scraper Offline"
            message = "The lead scraper has gone offline. New leads may not be detected until it's back online"
            priority = 'high'
        elif status == 'online':
            title = "Scraper Back Online"
            message = "The lead scraper is back online and actively monitoring for new leads"
            priority = 'normal'
        else:
            title = "Scraper Status Update"
            message = f"Scraper status changed to: {status}"
            priority = 'normal'
        
        return self.create_notification(
            user_id=user_id,
            notification_type='scraper_status',
            title=title,
            message=message,
            data=status_data,
            priority=priority
        )
    
    def _send_email_notification(self, user_id: int, title: str, message: str, 
                               data: Optional[Dict[Any, Any]] = None):
        """Send email notification to user"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("Email credentials not configured, skipping email notification")
            return
        
        try:
            # Get user email
            user = self.db.get_user(user_id)
            if not user or not user.get('email'):
                logger.warning(f"No email found for user {user_id}")
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = user['email']
            msg['Subject'] = f"LeadReplier: {title}"
            
            # Email body
            body = f"""
            Hi there,
            
            {message}
            
            You can view more details and manage your notifications in your LeadReplier dashboard.
            
            Best regards,
            The LeadReplier Team
            
            ---
            This is an automated notification. You can manage your email preferences in your account settings.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.from_email, user['email'], text)
            server.quit()
            
            logger.info(f"Email notification sent to {user['email']}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")

# Global notification service instance
notification_service = NotificationService()