#!/usr/bin/env python3
"""Test email connection and diagnose authentication issues."""

import imaplib
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def test_connection():
    """Test IMAP connection with detailed diagnostics."""
    print("=" * 60)
    print("Email Connection Diagnostic Tool")
    print("=" * 60)

    try:
        config = Config.from_env()
        print(f"\n✓ Configuration loaded")
        print(f"  Server: {config.email_server}")
        print(f"  Port: {config.email_port}")
        print(f"  Username: {config.email_username}")
        print(f"  Password: {'*' * len(config.email_password)}")

        print(f"\n[1/3] Testing server connection...")
        try:
            connection = imaplib.IMAP4_SSL(config.email_server, config.email_port)
            print(f"✓ Successfully connected to {config.email_server}:{config.email_port}")
        except Exception as e:
            print(f"✗ Failed to connect to server: {e}")
            print("\nPossible issues:")
            print("  - Check your internet connection")
            print("  - Verify the server address and port")
            print("  - Check if firewall is blocking the connection")
            return False

        print(f"\n[2/3] Testing authentication...")
        try:
            connection.login(config.email_username, config.email_password)
            print(f"✓ Successfully authenticated as {config.email_username}")
        except imaplib.IMAP4.error as e:
            print(f"✗ Authentication failed: {e}")
            print("\nFor Outlook/Office365 accounts, common issues:")
            print("  1. IMAP not enabled:")
            print("     → Go to Outlook.com → Settings → Mail → Sync email")
            print("     → Enable 'Let devices and apps use IMAP'")
            print("  2. Two-factor authentication enabled:")
            print("     → You need an app-specific password")
            print("     → Go to account.microsoft.com → Security → App passwords")
            print("     → Generate a new app password and use it in .env")
            print("  3. Basic authentication disabled:")
            print("     → Microsoft may have disabled basic auth for your account")
            print("     → You may need to enable it or use OAuth2")
            return False
        except Exception as e:
            print(f"✗ Unexpected error during authentication: {e}")
            return False

        print(f"\n[3/3] Testing mailbox access...")
        try:
            status, messages = connection.select("INBOX")
            if status == "OK":
                print(f"✓ Successfully accessed INBOX")
                print(f"  Total messages: {messages[0].decode()}")
            else:
                print(f"✗ Failed to access INBOX: {status}")
                return False
        except Exception as e:
            print(f"✗ Error accessing mailbox: {e}")
            return False

        print("\n" + "=" * 60)
        print("✓ All tests passed! Email connection is working.")
        print("=" * 60)

        connection.logout()
        return True

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
