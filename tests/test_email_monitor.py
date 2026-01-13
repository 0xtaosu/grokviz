"""Tests for email monitoring module."""

import pytest
from src.email_monitor import EmailParser


class TestEmailParser:
    """Tests for EmailParser class."""

    def test_parse_email_basic(self, mock_email):
        """Test basic email parsing."""
        parser = EmailParser()

        # Convert MIME message to bytes
        email_bytes = mock_email.as_bytes()

        # Parse email
        parsed = parser.parse_email(email_bytes)

        # Verify structure
        assert "subject" in parsed
        assert "from" in parsed
        assert "date" in parsed
        assert "html_body" in parsed
        assert "attachments" in parsed

        # Verify content
        assert "Grok Crypto Daily Digest" in parsed["subject"]
        assert "grok@example.com" in parsed["from"]

    def test_extract_json_attachment(self, mock_email):
        """Test JSON attachment extraction."""
        parser = EmailParser()

        email_bytes = mock_email.as_bytes()
        parsed = parser.parse_email(email_bytes)

        # Extract JSON
        json_data = parser.extract_json_attachment(parsed)

        # Verify JSON structure
        assert json_data is not None
        assert "date" in json_data
        assert "consensus_opportunities" in json_data
        assert "non_consensus_opportunities" in json_data

    def test_validate_grok_email(self, mock_email):
        """Test sender validation."""
        parser = EmailParser()

        email_bytes = mock_email.as_bytes()
        parsed = parser.parse_email(email_bytes)

        # Should validate successfully
        assert parser.validate_grok_email(parsed, "grok@example.com")

        # Should fail with different sender
        assert not parser.validate_grok_email(parsed, "other@example.com")

    def test_parse_email_without_json(self, mock_email_generator):
        """Test parsing email without JSON attachment."""
        parser = EmailParser()

        # Generate email without JSON
        email_msg = mock_email_generator.generate_mock_email(
            include_json=False,
            include_html=True
        )
        email_bytes = email_msg.as_bytes()

        parsed = parser.parse_email(email_bytes)

        # Should have HTML but no JSON attachment
        assert parsed["html_body"]
        assert len(parsed["attachments"]) == 0

        # Extract JSON should return None
        json_data = parser.extract_json_attachment(parsed)
        assert json_data is None
