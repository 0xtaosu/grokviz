"""Main workflow orchestration for GrokViz."""

import sys
import time
from pathlib import Path

from src.config import Config
from src.grok_client import GrokClient
from src.grok_client.prompts import CRYPTO_ANALYSIS_PROMPT
from src.data_processor import JSONProcessor
from src.infographic import InfographicGenerator
from src.telegram import TelegramBot
from src.utils.logger import setup_logger, get_logger
from src.utils.errors import (
    GrokVizError,
    GrokAPIError,
    DataProcessingError,
    InfographicGenerationError,
    TelegramSendError
)


def setup_logging(config: Config) -> None:
    """Setup application logging."""
    log_file = config.data_dir / "logs" / "grokviz.log"
    setup_logger(
        name="grokviz",
        log_level=config.log_level,
        log_file=log_file,
        log_to_console=True
    )


def archive_data(
    structured_data: dict,
    image_path: Path,
    config: Config
) -> None:
    """
    Archive processed data.

    Args:
        structured_data: Processed data
        image_path: Path to generated image
        config: Configuration
    """
    logger = get_logger(__name__)

    try:
        import json
        import shutil
        from datetime import datetime

        archive_dir = config.data_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Create dated subdirectory
        date_str = structured_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        date_archive = archive_dir / date_str
        date_archive.mkdir(parents=True, exist_ok=True)

        # Save structured data as JSON
        timestamp = datetime.now().strftime("%H%M%S")
        json_path = date_archive / f"{date_str}_{timestamp}_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)

        # Copy image to archive
        if image_path.exists():
            archive_image = date_archive / image_path.name
            shutil.copy2(image_path, archive_image)

        logger.debug(f"Archived data to {date_archive}")

    except Exception as e:
        logger.warning(f"Failed to archive data: {e}")


def main() -> int:
    """
    Main workflow orchestration.

    Returns:
        Exit code: 0 (success), 2 (failure)
    """
    start_time = time.time()
    logger = None

    try:
        # Step 1: Load configuration
        config = Config.from_env()

        # Step 2: Setup logging
        setup_logging(config)
        logger = get_logger(__name__)
        logger.info("=" * 60)
        logger.info("GrokViz workflow started")
        logger.info(f"Configuration: {config}")
        logger.info("=" * 60)

        # Step 3: Initialize components
        grok_client = GrokClient(
            api_key=config.grok_api_key,
            model=config.grok_model,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        json_processor = JSONProcessor()

        infographic_gen = InfographicGenerator(
            api_key=config.gemini_api_key,
            model_name=config.gemini_model,
            output_dir=config.temp_dir,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        telegram_bot = TelegramBot(
            token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        # Step 4: Call Grok API to generate report
        logger.info("Calling Grok API to generate crypto analysis report...")
        raw_data = grok_client.generate_report(
            CRYPTO_ANALYSIS_PROMPT,
            timeout=config.grok_timeout
        )
        logger.info("Grok API call successful")

        # Step 5: Process and validate data
        logger.info("Processing and validating data...")
        structured_data = json_processor.process(raw_data)
        logger.info(f"Data processed: {structured_data.get('date')}")

        # Step 6: Generate infographic
        logger.info("Generating infographic...")
        image_path = infographic_gen.generate(structured_data, timeout=120)
        logger.info(f"Infographic generated: {image_path}")

        # Step 7: Send to Telegram
        logger.info("Sending to Telegram...")
        caption = telegram_bot.format_caption(structured_data)
        message_id = telegram_bot.send_photo(image_path, caption)
        logger.info(f"Sent to Telegram: message_id={message_id}")

        # Step 8: Archive data (optional)
        if config.archive_reports:
            archive_data(structured_data, image_path, config)

        # Step 9: Log success
        duration = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Workflow completed successfully in {duration:.2f}s")
        logger.info("=" * 60)

        return 0

    except GrokAPIError as e:
        if logger:
            logger.critical(f"Grok API error: {e}", exc_info=True)
        else:
            print(f"GROK API ERROR: {e}", file=sys.stderr)
        return 2

    except DataProcessingError as e:
        if logger:
            logger.critical(f"Data processing error: {e}", exc_info=True)
        else:
            print(f"DATA PROCESSING ERROR: {e}", file=sys.stderr)
        return 2

    except InfographicGenerationError as e:
        if logger:
            logger.critical(f"Infographic generation error: {e}", exc_info=True)
        else:
            print(f"INFOGRAPHIC ERROR: {e}", file=sys.stderr)
        return 2

    except TelegramSendError as e:
        if logger:
            logger.critical(f"Telegram send error: {e}", exc_info=True)
        else:
            print(f"TELEGRAM ERROR: {e}", file=sys.stderr)
        return 2

    except Exception as e:
        if logger:
            logger.critical(f"Workflow failed with unexpected error: {e}", exc_info=True)
        else:
            print(f"CRITICAL ERROR: {e}", file=sys.stderr)
        return 2

    finally:
        if logger:
            total_time = time.time() - start_time
            logger.info(f"Total execution time: {total_time:.2f}s")


if __name__ == "__main__":
    sys.exit(main())
