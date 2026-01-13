"""Tests for Telegram bot module."""

import pytest
from src.telegram import TelegramBot


class TestTelegramBot:
    """Tests for TelegramBot class."""

    def test_format_caption(self, mock_json_data):
        """Test caption formatting."""
        from src.data_processor import JSONProcessor

        # Process data first
        processor = JSONProcessor()
        normalized = processor.normalize_data(mock_json_data)

        # Create bot (with dummy credentials for testing)
        bot = TelegramBot(
            token="123456:ABC-DEF",
            chat_id="-1001234567890"
        )

        # Format caption
        caption = bot.format_caption(normalized)

        # Verify caption structure
        assert "Grok Crypto Daily Digest" in caption
        assert normalized["date"] in caption
        assert "Consensus Opportunity" in caption
        assert "Non-Consensus Opportunity" in caption
        assert "#GrokDaily" in caption

    def test_caption_length(self, mock_json_data):
        """Test caption is reasonable length."""
        from src.data_processor import JSONProcessor

        processor = JSONProcessor()
        normalized = processor.normalize_data(mock_json_data)

        bot = TelegramBot(
            token="123456:ABC-DEF",
            chat_id="-1001234567890"
        )

        caption = bot.format_caption(normalized)

        # Telegram caption limit is 1024 characters
        # Our caption should be well under that
        assert len(caption) < 500


# Note: Full integration test for send_photo requires actual Telegram bot
# and will be tested in integration tests
