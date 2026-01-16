#!/usr/bin/env python3
"""Standalone script to send a mock Grok email to your inbox for testing."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from tests.mock_email_generator import MockEmailGenerator
from src.utils.logger import setup_logger


def main():
    """Send mock email to configured inbox."""
    # Setup logger
    logger = setup_logger("mock_email_generator", log_level="INFO")

    try:
        # Load configuration
        logger.info("Loading configuration")
        config = Config.from_env()

        # Create generator
        generator = MockEmailGenerator()

        # For sending, we need SMTP credentials
        # Gmail users: use smtp.gmail.com, port 587, app password
        # This is a simplified version - update based on your email provider

        logger.info("Please provide SMTP credentials for sending test email:")
        smtp_server = input("SMTP server (e.g., smtp.gmail.com): ").strip()
        smtp_port = int(input("SMTP port (e.g., 587): ").strip())
        smtp_username = input("SMTP username: ").strip()
        smtp_password = input("SMTP password: ").strip()

        # Send to the configured email address
        to_email = config.email_username

        logger.info(f"Sending mock email to {to_email}")

        generator.send_mock_email_to_inbox(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            to_email=to_email,
            include_json=True,
            include_html=True
        )

        logger.info("✅ Mock email sent successfully!")
        logger.info(f"Check your inbox: {to_email}")
        logger.info("The email should appear as unread from grok@example.com")

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to send mock email: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
