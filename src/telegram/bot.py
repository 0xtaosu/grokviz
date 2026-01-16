"""Telegram bot for sending infographics to channels/chats."""

import asyncio
import time
from pathlib import Path
from typing import Dict, Any, Optional

from telegram import Bot
from telegram.error import TelegramError

from src.utils.errors import TelegramSendError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramBot:
    """Telegram bot for sending crypto daily infographics."""

    def __init__(
        self,
        token: str,
        chat_id: str,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize Telegram bot.

        Args:
            token: Telegram bot token
            chat_id: Target chat/channel ID
            max_retries: Maximum retry attempts for sending
            retry_delay: Base delay between retries in seconds
        """
        self.token = token
        self.chat_id = chat_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        try:
            self.bot = Bot(token=self.token)
            logger.info(f"Telegram bot initialized for chat: {self.chat_id}")
        except Exception as e:
            raise TelegramSendError(
                f"Failed to initialize Telegram bot: {e}",
                context={"error": str(e)}
            )

    def send_photo(
        self,
        image_path: Path,
        caption: Optional[str] = None
    ) -> str:
        """
        Send photo to Telegram chat.

        Args:
            image_path: Path to image file
            caption: Optional caption text

        Returns:
            Message ID of sent message

        Raises:
            TelegramSendError: If sending fails after all retries
        """
        if not image_path.exists():
            raise TelegramSendError(
                f"Image file not found: {image_path}",
                context={"image_path": str(image_path)}
            )

        # Verify file size (Telegram limit: 10MB for photos)
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            logger.warning(
                f"Image size {file_size_mb:.2f}MB exceeds Telegram photo limit (10MB). "
                "Sending as document instead."
            )
            return self._send_document_with_retry(image_path, caption)

        return self._send_photo_with_retry(image_path, caption)

    def _send_photo_with_retry(
        self,
        image_path: Path,
        caption: Optional[str]
    ) -> str:
        """Send photo with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending photo to Telegram (attempt {attempt + 1}/{self.max_retries})")

                with open(image_path, "rb") as photo_file:
                    message = asyncio.run(self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo_file,
                        caption=caption,
                        parse_mode="Markdown"
                    ))

                message_id = str(message.message_id)
                logger.info(
                    f"Photo sent successfully: message_id={message_id}",
                    extra={"message_id": message_id, "chat_id": self.chat_id}
                )

                return message_id

            except TelegramError as e:
                last_error = e
                if attempt == self.max_retries - 1:
                    break

                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Telegram send failed (attempt {attempt + 1}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

        raise TelegramSendError(
            f"Failed to send photo after {self.max_retries} attempts: {last_error}",
            context={
                "attempts": self.max_retries,
                "chat_id": self.chat_id,
                "error": str(last_error)
            }
        )

    def _send_document_with_retry(
        self,
        image_path: Path,
        caption: Optional[str]
    ) -> str:
        """Send as document (for larger files) with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Sending document to Telegram (attempt {attempt + 1}/{self.max_retries})")

                with open(image_path, "rb") as doc_file:
                    message = asyncio.run(self.bot.send_document(
                        chat_id=self.chat_id,
                        document=doc_file,
                        caption=caption,
                        parse_mode="Markdown"
                    ))

                message_id = str(message.message_id)
                logger.info(f"Document sent successfully: message_id={message_id}")

                return message_id

            except TelegramError as e:
                last_error = e
                if attempt == self.max_retries - 1:
                    break

                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Telegram send failed (attempt {attempt + 1}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

        raise TelegramSendError(
            f"Failed to send document after {self.max_retries} attempts: {last_error}",
            context={
                "attempts": self.max_retries,
                "chat_id": self.chat_id,
                "error": str(last_error)
            }
        )

    def format_caption(self, data: Dict[str, Any]) -> str:
        """
        Format caption for Telegram message.

        Args:
            data: Processed data from JSON processor

        Returns:
            Formatted caption string
        """
        date = data.get("date", "")
        consensus_opps = data.get("consensus_opportunities", [])
        non_consensus_opps = data.get("non_consensus_opportunities", [])

        # Get top opportunities
        consensus_top = consensus_opps[0].get("name", "") if consensus_opps else "N/A"
        non_consensus_top = non_consensus_opps[0].get("name", "") if non_consensus_opps else "N/A"

        caption = f"""🚀 *Grok Crypto Daily Digest* - {date}

📊 *Today's Highlights:*

🔥 *Consensus Opportunity:* {consensus_top}
💎 *Non-Consensus Opportunity:* {non_consensus_top}

📈 *Total Opportunities:*
• Consensus: {len(consensus_opps)}
• Non-Consensus: {len(non_consensus_opps)}

#GrokDaily #CryptoInsights #Web3 #AI
"""

        return caption

    def send_message(self, text: str) -> str:
        """
        Send text message to Telegram chat.

        Args:
            text: Message text

        Returns:
            Message ID

        Raises:
            TelegramSendError: If sending fails
        """
        try:
            message = self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode="Markdown"
            )
            return str(message.message_id)
        except TelegramError as e:
            raise TelegramSendError(
                f"Failed to send message: {e}",
                context={"error": str(e)}
            )

    def test_connection(self) -> bool:
        """
        Test bot connection and permissions.

        Returns:
            True if connection is successful

        Raises:
            TelegramSendError: If test fails
        """
        try:
            bot_info = self.bot.get_me()
            logger.info(f"Bot connection test successful: @{bot_info.username}")

            # Try to get chat info
            chat = self.bot.get_chat(self.chat_id)
            logger.info(f"Target chat accessible: {chat.type} - {chat.title or chat.id}")

            return True

        except TelegramError as e:
            raise TelegramSendError(
                f"Bot connection test failed: {e}",
                context={"error": str(e)}
            )
