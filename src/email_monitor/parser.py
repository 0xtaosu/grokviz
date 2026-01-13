"""Email parser for extracting content and attachments from emails."""

import email
import json
from email.message import Message
from typing import Dict, List, Optional, Any

from src.utils.errors import EmailParseError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmailParser:
    """Parser for extracting data from email messages."""

    def parse_email(self, raw_email: bytes) -> Dict[str, Any]:
        """
        Parse raw email data into structured format.

        Args:
            raw_email: Raw email bytes (RFC822 format)

        Returns:
            Dictionary containing:
                - subject: Email subject
                - from: Sender email address
                - date: Email date
                - html_body: HTML content
                - plain_body: Plain text content
                - attachments: List of attachments

        Raises:
            EmailParseError: If parsing fails
        """
        try:
            # Parse email message
            msg = email.message_from_bytes(raw_email)

            # Extract headers
            subject = self._decode_header(msg.get("Subject", ""))
            from_addr = self._decode_header(msg.get("From", ""))
            date = msg.get("Date", "")

            logger.debug(f"Parsing email: {subject} from {from_addr}")

            # Extract body and attachments
            html_body = ""
            plain_body = ""
            attachments = []

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    # Extract body
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        plain_body = self._get_payload(part)
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        html_body = self._get_payload(part)

                    # Extract attachments
                    elif "attachment" in content_disposition or part.get_filename():
                        filename = part.get_filename()
                        if filename:
                            attachment_data = part.get_payload(decode=True)
                            attachments.append({
                                "filename": filename,
                                "content_type": content_type,
                                "content": attachment_data
                            })
                            logger.debug(f"Found attachment: {filename} ({content_type})")
            else:
                # Non-multipart message
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    plain_body = self._get_payload(msg)
                elif content_type == "text/html":
                    html_body = self._get_payload(msg)

            return {
                "subject": subject,
                "from": from_addr,
                "date": date,
                "html_body": html_body,
                "plain_body": plain_body,
                "attachments": attachments
            }

        except Exception as e:
            raise EmailParseError(
                f"Failed to parse email: {e}",
                context={"error": str(e)}
            )

    def extract_json_attachment(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON attachment from email.

        Args:
            email_data: Parsed email data from parse_email()

        Returns:
            Parsed JSON data or None if no JSON attachment found

        Raises:
            EmailParseError: If JSON parsing fails
        """
        attachments = email_data.get("attachments", [])

        for attachment in attachments:
            filename = attachment.get("filename", "")
            if filename.endswith(".json"):
                try:
                    content = attachment["content"]
                    if isinstance(content, bytes):
                        content = content.decode("utf-8")

                    json_data = json.loads(content)
                    logger.info(f"Successfully parsed JSON attachment: {filename}")
                    return json_data

                except json.JSONDecodeError as e:
                    raise EmailParseError(
                        f"Failed to parse JSON attachment '{filename}': {e}",
                        context={"filename": filename, "error": str(e)}
                    )
                except Exception as e:
                    raise EmailParseError(
                        f"Error reading JSON attachment '{filename}': {e}",
                        context={"filename": filename, "error": str(e)}
                    )

        logger.warning("No JSON attachment found in email")
        return None

    @staticmethod
    def _decode_header(header: str) -> str:
        """Decode email header."""
        if not header:
            return ""

        decoded_parts = email.header.decode_header(header)
        result = []

        for content, encoding in decoded_parts:
            if isinstance(content, bytes):
                if encoding:
                    result.append(content.decode(encoding, errors="replace"))
                else:
                    result.append(content.decode("utf-8", errors="replace"))
            else:
                result.append(str(content))

        return "".join(result)

    @staticmethod
    def _get_payload(part: Message) -> str:
        """Extract and decode email part payload."""
        try:
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                # Try to decode with charset from content-type
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
            return str(payload)
        except Exception as e:
            logger.warning(f"Error decoding payload: {e}")
            return ""

    def validate_grok_email(self, email_data: Dict[str, Any], expected_sender: str) -> bool:
        """
        Validate that email is from Grok.

        Args:
            email_data: Parsed email data
            expected_sender: Expected sender email address

        Returns:
            True if email is from expected sender, False otherwise
        """
        from_addr = email_data.get("from", "").lower()
        expected_sender = expected_sender.lower()

        is_valid = expected_sender in from_addr
        if not is_valid:
            logger.warning(
                f"Email from '{from_addr}' does not match expected sender '{expected_sender}'"
            )

        return is_valid
