"""
Module to handle notifications for jobs
"""
import logging
import smtplib
import requests
from typing import Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


def send_notification(job: Dict, config: Dict) -> bool:
    """
    Send notification for a job
    
    Args:
        job: Job dictionary
        config: Configuration dictionary
        
    Returns:
        True if notification sent successfully, False otherwise
    """
    try:
        notification_type = config.get("notification_type", "email")
        
        if notification_type == "email":
            return send_email_notification(job, config)
        elif notification_type == "slack":
            return send_slack_notification(job, config)
        elif notification_type == "webhook":
            return send_webhook_notification(job, config)
        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False


def send_email_notification(job: Dict, config: Dict) -> bool:
    """Send email notification"""
    try:
        recipient = config.get("email_recipient")
        sender = config.get("email_sender")
        smtp_server = config.get("smtp_server")
        smtp_port = config.get("smtp_port")
        smtp_password = config.get("smtp_password")

        if not all([recipient, sender, smtp_server, smtp_port, smtp_password]):
            logger.warning("Email config incomplete - skipping notification")
            return False

        # Type assertions after validation
        assert recipient is not None
        assert sender is not None
        assert smtp_server is not None
        assert smtp_port is not None
        assert smtp_password is not None

        # Create email
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = f"New Job Alert: {job.get('title')}"

        body = f"""New matching job found!

Title: {job.get('title')}
Location: {job.get('location')}
URL: {job.get('url')}

Check it out before others do!
"""
        msg.attach(MIMEText(body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent for job: {job.get('title')}")
        return True

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False


def send_slack_notification(job: Dict, config: Dict) -> bool:
    """Send Slack notification"""
    try:
        slack_webhook = config.get("slack_webhook")
        
        if not slack_webhook:
            logger.warning("Slack webhook not configured - skipping notification")
            return False
        
        message = {
            "text": f"New Job Alert: {job.get('title')}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Job Found!*\n*Title:* {job.get('title')}\n*Location:* {job.get('location')}\n*URL:* <{job.get('url')}|View Job>"
                    }
                }
            ]
        }
        
        response = requests.post(slack_webhook, json=message, timeout=5)
        response.raise_for_status()
        
        logger.info(f"Slack notification sent for job: {job.get('title')}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        return False


def send_webhook_notification(job: Dict, config: Dict) -> bool:
    """Send generic webhook notification"""
    try:
        webhook_url = config.get("webhook_url")
        
        if not webhook_url:
            logger.warning("Webhook URL not configured - skipping notification")
            return False
        
        payload = {
            "title": job.get('title'),
            "location": job.get('location'),
            "url": job.get('url'),
            "type": "job_alert"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        
        logger.info(f"Webhook notification sent for job: {job.get('title')}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending webhook notification: {str(e)}")
        return False
