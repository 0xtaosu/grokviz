#!/usr/bin/env python3
"""End-to-end test of the complete workflow (without Grok API)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.config import Config
from src.data_processor import JSONProcessor
from src.infographic import InfographicGenerator
from src.telegram import TelegramBot
from tests.mock_email_generator import MockEmailGenerator
from src.utils.logger import setup_logger, get_logger

def main():
    """Run end-to-end test."""
    print("=" * 70)
    print("GrokViz End-to-End Workflow Test")
    print("(Mock Data → Data Processing → Infographic → Telegram)")
    print("=" * 70)

    # Load configuration
    load_dotenv()
    config = Config.from_env()

    # Setup logging
    setup_logger(
        name="grokviz",
        log_level=config.log_level,
        log_to_console=True
    )
    logger = get_logger(__name__)

    try:
        # Step 1: Generate mock data
        print("\n" + "-" * 70)
        print("Step 1: Generating mock Grok daily report data...")
        print("-" * 70)

        mock_generator = MockEmailGenerator()
        raw_data = mock_generator.generate_json_attachment()

        print(f"✓ Generated mock data:")
        print(f"  - Date: {raw_data['date']}")
        print(f"  - Consensus opportunities: {len(raw_data['consensus_opportunities'])}")
        print(f"  - Non-consensus opportunities: {len(raw_data['non_consensus_opportunities'])}")

        # Step 2: Process data
        print("\n" + "-" * 70)
        print("Step 2: Processing and validating data...")
        print("-" * 70)

        json_processor = JSONProcessor()
        processed_data = json_processor.process(raw_data)

        print(f"✓ Data validated and normalized")

        # Step 3: Generate infographic
        print("\n" + "-" * 70)
        print("Step 3: Generating infographic with Gemini API...")
        print("-" * 70)
        print("This may take 30-60 seconds...")

        infographic_gen = InfographicGenerator(
            api_key=config.gemini_api_key,
            model_name=config.gemini_model,
            output_dir=config.temp_dir,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        image_path = infographic_gen.generate(processed_data, timeout=120)

        print(f"\n✓ Infographic generated:")
        print(f"  - Path: {image_path}")
        print(f"  - Size: {image_path.stat().st_size / 1024:.1f} KB")

        # Verify image
        from PIL import Image
        img = Image.open(image_path)
        width, height = img.size
        print(f"  - Dimensions: {width}x{height}px")

        # Step 4: Send to Telegram
        print("\n" + "-" * 70)
        print("Step 4: Sending to Telegram...")
        print("-" * 70)

        telegram_bot = TelegramBot(
            token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        caption = telegram_bot.format_caption(processed_data)
        print(f"\nCaption preview:")
        print(f"  {caption[:200]}...")

        message_id = telegram_bot.send_photo(image_path, caption)

        print(f"\n✓ Sent to Telegram:")
        print(f"  - Message ID: {message_id}")
        print(f"  - Chat ID: {config.telegram_chat_id}")

        # Success!
        print("\n" + "=" * 70)
        print("✅ END-TO-END TEST PASSED!")
        print("=" * 70)
        print(f"\nWorkflow completed successfully:")
        print(f"  1. ✓ Mock data generated")
        print(f"  2. ✓ Data processed and validated")
        print(f"  3. ✓ Infographic generated via Gemini API")
        print(f"  4. ✓ Message sent to Telegram")
        print(f"\nCheck your Telegram channel to view the infographic!")

        return 0

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        print(f"\n❌ TEST FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
