#!/usr/bin/env python3
"""Test script to generate infographic from JSON data without email."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.data_processor import JSONProcessor
from src.infographic import InfographicGenerator
from src.telegram import TelegramBot
from src.utils.logger import setup_logger
from tests.mock_email_generator import MockEmailGenerator


def main():
    """Test infographic generation and Telegram sending."""
    # Setup logger
    log_file = Path("data/logs/test_grokviz.log")
    logger = setup_logger("test_grokviz", log_level="INFO", log_file=log_file)

    logger.info("=" * 60)
    logger.info("GrokViz Test - Skipping Email, Testing Gemini + Telegram")
    logger.info("=" * 60)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config.from_env()

        # Generate mock data
        logger.info("Generating mock Grok data...")
        generator = MockEmailGenerator()
        json_data = generator.generate_json_attachment()

        # Process data
        logger.info("Processing JSON data...")
        processor = JSONProcessor()
        structured_data = processor.process_attachment(json_data)
        logger.info(f"Data processed: {structured_data.get('date')}")

        # Generate infographic
        logger.info("Generating infographic via Gemini API...")
        infographic_gen = InfographicGenerator(
            api_key=config.gemini_api_key,
            model_name=config.gemini_model,
            output_dir=config.temp_dir,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        image_path = infographic_gen.generate(structured_data, timeout=120)
        logger.info(f"✅ Infographic generated: {image_path}")

        # Send to Telegram
        logger.info("Sending to Telegram...")
        telegram_bot = TelegramBot(
            token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        caption = telegram_bot.format_caption(structured_data)
        message_id = telegram_bot.send_photo(image_path, caption)
        logger.info(f"✅ Sent to Telegram: message_id={message_id}")

        logger.info("=" * 60)
        logger.info("✅ TEST SUCCESSFUL!")
        logger.info("=" * 60)
        logger.info("Next steps:")
        logger.info("1. Check your Telegram for the infographic")
        logger.info("2. Verify the image quality and content")
        logger.info("3. Fix email authentication to enable full automation")

        return 0

    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
