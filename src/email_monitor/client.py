"""IMAP email client for fetching Grok daily emails."""

import imaplib
import time
from typing import List, Tuple, Optional

from src.utils.errors import EmailFetchError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmailClient:
    """IMAP client for connecting to email server and fetching emails."""

    def __init__(
        self,
        server: str,
        port: int,
        username: str,
        password: str,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize email client.

        Args:
            server: IMAP server address
            port: IMAP server port (typically 993 for SSL)
            username: Email account username
            password: Email account password
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """
        Establish connection to IMAP server with retry logic.

        Raises:
            EmailFetchError: If connection fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Connecting to IMAP server {self.server}:{self.port} (attempt {attempt + 1})")
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
                self.connection.login(self.username, self.password)
                logger.info("Successfully connected to IMAP server")
                return
            except imaplib.IMAP4.error as e:
                if attempt == self.max_retries - 1:
                    raise EmailFetchError(
                        f"Failed to connect to IMAP server after {self.max_retries} attempts",
                        context={"server": self.server, "port": self.port, "error": str(e)}
                    )
                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
            except Exception as e:
                raise EmailFetchError(
                    f"Unexpected error connecting to IMAP server: {e}",
                    context={"server": self.server, "port": self.port, "error": str(e)}
                )

    def disconnect(self) -> None:
        """Close connection to IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
                logger.info("Disconnected from IMAP server")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self.connection = None

    def fetch_unread_emails(
        self,
        sender_filter: Optional[str] = None,
        mailbox: str = "INBOX"
    ) -> List[Tuple[str, bytes]]:
        """
        Fetch unread emails from the specified mailbox.

        Args:
            sender_filter: Filter emails by sender address (optional)
            mailbox: Mailbox to search (default: INBOX)

        Returns:
            List of tuples (email_id, raw_email_data)

        Raises:
            EmailFetchError: If fetching emails fails
        """
        if not self.connection:
            raise EmailFetchError("Not connected to IMAP server")

        try:
            # Select mailbox
            status, messages = self.connection.select(mailbox)
            if status != "OK":
                raise EmailFetchError(
                    f"Failed to select mailbox '{mailbox}'",
                    context={"mailbox": mailbox, "status": status}
                )

            # Build search criteria
            if sender_filter:
                search_criteria = f'(UNSEEN FROM "{sender_filter}")'
            else:
                search_criteria = "(UNSEEN)"

            # Search for emails
            status, message_ids = self.connection.search(None, search_criteria)
            if status != "OK":
                raise EmailFetchError(
                    f"Failed to search emails with criteria: {search_criteria}",
                    context={"criteria": search_criteria, "status": status}
                )

            # Parse message IDs
            email_ids = message_ids[0].split()
            if not email_ids:
                logger.info(f"No unread emails found with criteria: {search_criteria}")
                return []

            logger.info(f"Found {len(email_ids)} unread email(s)")

            # Fetch each email
            emails = []
            for email_id in email_ids:
                try:
                    status, msg_data = self.connection.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        logger.warning(f"Failed to fetch email ID {email_id}")
                        continue

                    raw_email = msg_data[0][1]
                    emails.append((email_id.decode(), raw_email))
                except Exception as e:
                    logger.warning(f"Error fetching email ID {email_id}: {e}")
                    continue

            return emails

        except imaplib.IMAP4.error as e:
            raise EmailFetchError(
                f"IMAP error while fetching emails: {e}",
                context={"mailbox": mailbox, "error": str(e)}
            )
        except Exception as e:
            raise EmailFetchError(
                f"Unexpected error while fetching emails: {e}",
                context={"mailbox": mailbox, "error": str(e)}
            )

    def mark_as_read(self, email_id: str) -> None:
        """
        Mark an email as read.

        Args:
            email_id: Email ID to mark as read

        Raises:
            EmailFetchError: If marking fails
        """
        if not self.connection:
            raise EmailFetchError("Not connected to IMAP server")

        try:
            status, _ = self.connection.store(email_id, "+FLAGS", "\\Seen")
            if status != "OK":
                raise EmailFetchError(
                    f"Failed to mark email as read",
                    context={"email_id": email_id, "status": status}
                )
            logger.debug(f"Marked email {email_id} as read")
        except Exception as e:
            raise EmailFetchError(
                f"Error marking email as read: {e}",
                context={"email_id": email_id, "error": str(e)}
            )

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
