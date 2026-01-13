"""Main workflow orchestration for GrokViz."""

import sys
import time
from pathlib import Path
from typing import Optional

from src.config import Config
from src.email_monitor import EmailClient, EmailParser
from src.data_processor import JSONProcessor, HTMLParser
from src.infographic import InfographicGenerator
from src.telegram import TelegramBot
from src.utils.logger import setup_logger, get_logger
from src.utils.errors import (
    GrokVizError,
    EmailFetchError,
    EmailParseError,
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


def process_email(
    email_id: str,
    raw_email: bytes,
    email_parser: EmailParser,
    json_processor: JSONProcessor,
    html_parser: HTMLParser,
    infographic_gen: InfographicGenerator,
    telegram_bot: TelegramBot,
    email_client: EmailClient,
    config: Config
) -> bool:
    """
    Process a single email through the complete workflow.

    Args:
        email_id: Email ID
        raw_email: Raw email data
        email_parser: Email parser instance
        json_processor: JSON processor instance
        html_parser: HTML parser instance
        infographic_gen: Infographic generator instance
        telegram_bot: Telegram bot instance
        email_client: Email client instance
        config: Configuration

    Returns:
        True if processing succeeded, False otherwise
    """
    logger = get_logger(__name__)

    try:
        # Step 1: Parse email
        logger.info(f"Processing email ID: {email_id}")
        email_data = email_parser.parse_email(raw_email)
        logger.info(f"Email parsed: {email_data['subject']}")

        # Validate sender
        if not email_parser.validate_grok_email(email_data, config.grok_sender_email):
            logger.warning(f"Email from unexpected sender, skipping: {email_data['from']}")
            return False

        # Step 2: Extract data (JSON preferred, HTML fallback)
        structured_data = None

        # Try JSON attachment first
        json_attachment = email_parser.extract_json_attachment(email_data)
        if json_attachment:
            logger.info("Processing data from JSON attachment")
            structured_data = json_processor.process_attachment(json_attachment)
        else:
            # Fallback to HTML parsing
            logger.warning("No JSON attachment found, falling back to HTML parsing")
            if email_data.get("html_body"):
                structured_data = html_parser.parse_html(email_data["html_body"])
            else:
                raise DataProcessingError(
                    "No JSON attachment or HTML body found in email",
                    context={"email_id": email_id}
                )

        logger.info(f"Data processed: {structured_data.get('date')}")

        # Step 3: Generate infographic
        logger.info("Generating infographic...")
        image_path = infographic_gen.generate(structured_data, timeout=120)
        logger.info(f"Infographic generated: {image_path}")

        # Step 4: Send to Telegram
        logger.info("Sending to Telegram...")
        caption = telegram_bot.format_caption(structured_data)
        message_id = telegram_bot.send_photo(image_path, caption)
        logger.info(f"Sent to Telegram: message_id={message_id}")

        # Step 5: Mark email as read
        email_client.mark_as_read(email_id)
        logger.info(f"Email {email_id} marked as read")

        # Step 6: Archive (optional)
        if config.archive_emails:
            archive_data(email_id, email_data, structured_data, image_path, config)

        logger.info(f"Successfully processed email {email_id}")
        return True

    except EmailParseError as e:
        logger.error(f"Email parsing failed for {email_id}: {e}", exc_info=True)
        return False
    except DataProcessingError as e:
        logger.error(f"Data processing failed for {email_id}: {e}", exc_info=True)
        return False
    except InfographicGenerationError as e:
        logger.error(f"Infographic generation failed for {email_id}: {e}", exc_info=True)
        return False
    except TelegramSendError as e:
        logger.error(f"Telegram send failed for {email_id}: {e}", exc_info=True)
        # Don't mark as read if Telegram send fails
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing email {email_id}: {e}", exc_info=True)
        return False


def archive_data(
    email_id: str,
    email_data: dict,
    structured_data: dict,
    image_path: Path,
    config: Config
) -> None:
    """
    Archive processed email data.

    Args:
        email_id: Email ID
        email_data: Parsed email data
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
        json_path = date_archive / f"{email_id}_data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)

        # Copy image to archive
        if image_path.exists():
            archive_image = date_archive / image_path.name
            shutil.copy2(image_path, archive_image)

        logger.debug(f"Archived data for email {email_id} to {date_archive}")

    except Exception as e:
        logger.warning(f"Failed to archive data for {email_id}: {e}")


def main() -> int:
    """
    Main workflow orchestration.

    Returns:
        Exit code: 0 (success), 1 (partial failure), 2 (complete failure)
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
        email_client = EmailClient(
            server=config.email_server,
            port=config.email_port,
            username=config.email_username,
            password=config.email_password,
            max_retries=config.max_retries,
            retry_delay=config.retry_delay
        )

        email_parser = EmailParser()
        json_processor = JSONProcessor()
        html_parser = HTMLParser()

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

        # Step 4: Connect to email server
        email_client.connect()

        # Step 5: Fetch unread emails from Grok
        emails = email_client.fetch_unread_emails(
            sender_filter=config.grok_sender_email
        )

        if not emails:
            logger.info("No new emails from Grok. Workflow complete.")
            email_client.disconnect()
            return 0

        logger.info(f"Found {len(emails)} unread email(s) to process")

        # Step 6: Process each email
        success_count = 0
        failure_count = 0

        for email_id, raw_email in emails:
            success = process_email(
                email_id=email_id,
                raw_email=raw_email,
                email_parser=email_parser,
                json_processor=json_processor,
                html_parser=html_parser,
                infographic_gen=infographic_gen,
                telegram_bot=telegram_bot,
                email_client=email_client,
                config=config
            )

            if success:
                success_count += 1
            else:
                failure_count += 1

        # Step 7: Cleanup
        email_client.disconnect()

        # Step 8: Log summary
        duration = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Workflow completed in {duration:.2f}s")
        logger.info(f"Success: {success_count}, Failures: {failure_count}")
        logger.info("=" * 60)

        # Determine exit code
        if failure_count == 0:
            return 0  # All succeeded
        elif success_count > 0:
            return 1  # Partial failure
        else:
            return 2  # Complete failure

    except EmailFetchError as e:
        if logger:
            logger.critical(f"Email fetch error: {e}", exc_info=True)
        else:
            print(f"EMAIL FETCH ERROR: {e}", file=sys.stderr)
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
