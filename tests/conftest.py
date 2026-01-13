"""Pytest configuration and fixtures for GrokViz tests."""

import pytest
from pathlib import Path
from tests.mock_email_generator import MockEmailGenerator


@pytest.fixture
def mock_config():
    """Provide mock configuration for testing."""
    from src.config import Config
    import os

    # Set test environment variables
    os.environ["EMAIL_SERVER"] = "imap.test.com"
    os.environ["EMAIL_PORT"] = "993"
    os.environ["EMAIL_USERNAME"] = "test@test.com"
    os.environ["EMAIL_PASSWORD"] = "test_password"
    os.environ["GROK_SENDER_EMAIL"] = "grok@example.com"
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    os.environ["GEMINI_MODEL"] = "gemini-1.5-pro"
    os.environ["TELEGRAM_BOT_TOKEN"] = "123456:ABC-DEF"
    os.environ["TELEGRAM_CHAT_ID"] = "-1001234567890"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["DATA_DIR"] = "/tmp/grokviz_test"
    os.environ["TEMP_DIR"] = "/tmp/grokviz_test/temp"
    os.environ["ARCHIVE_EMAILS"] = "false"

    return Config()


@pytest.fixture
def mock_email_generator():
    """Provide mock email generator."""
    return MockEmailGenerator()


@pytest.fixture
def mock_email(mock_email_generator):
    """Provide a mock email message."""
    return mock_email_generator.generate_mock_email(include_json=True, include_html=True)


@pytest.fixture
def mock_json_data(mock_email_generator):
    """Provide mock JSON data."""
    return mock_email_generator.generate_json_attachment()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
