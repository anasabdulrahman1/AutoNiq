"""
Configuration management module
"""
import os
import json
import logging
from typing import Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def load_config() -> Dict:
    """
    Load configuration from environment variables and config file
    
    Returns:
        Configuration dictionary
    """
    config = {
        "notification_type": os.getenv("NOTIFICATION_TYPE", "email"),
        "api_url": os.getenv("API_URL", ""),
        "api_key": os.getenv("API_KEY", ""),
        "email_recipient": os.getenv("EMAIL_RECIPIENT", ""),
        "email_sender": os.getenv("EMAIL_SENDER", ""),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "slack_webhook": os.getenv("SLACK_WEBHOOK", ""),
        "webhook_url": os.getenv("WEBHOOK_URL", ""),
        "update_interval": int(os.getenv("UPDATE_INTERVAL", "3600")),
    }
    
    logger.info("Configuration loaded successfully")
    return config


def get_config_value(key: str, default=None):
    """
    Get a specific configuration value
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    config = load_config()
    return config.get(key, default)
