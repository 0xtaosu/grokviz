"""Tests for data processing module."""

import pytest
from src.data_processor import JSONProcessor, HTMLParser
from src.utils.errors import DataProcessingError


class TestJSONProcessor:
    """Tests for JSONProcessor class."""

    def test_process_valid_json(self, mock_json_data):
        """Test processing valid JSON data."""
        processor = JSONProcessor()

        result = processor.process_attachment(mock_json_data)

        # Verify structure
        assert "date" in result
        assert "consensus_opportunities" in result
        assert "non_consensus_opportunities" in result
        assert "macro_indicators" in result

        # Verify normalization
        assert isinstance(result["consensus_opportunities"], list)
        assert isinstance(result["non_consensus_opportunities"], list)

    def test_validate_structure_valid(self, mock_json_data):
        """Test structure validation with valid data."""
        processor = JSONProcessor()

        # Should not raise exception
        processor.validate_structure(mock_json_data)

    def test_validate_structure_missing_date(self):
        """Test validation fails when date is missing."""
        processor = JSONProcessor()

        invalid_data = {
            "consensus_opportunities": []
        }

        with pytest.raises(DataProcessingError):
            processor.validate_structure(invalid_data)

    def test_extract_summary(self, mock_json_data):
        """Test summary extraction."""
        processor = JSONProcessor()
        normalized = processor.normalize_data(mock_json_data)

        summary = processor.extract_summary(normalized)

        assert "date" in summary
        assert "consensus_count" in summary
        assert "non_consensus_count" in summary
        assert "consensus_top" in summary
        assert "non_consensus_top" in summary


class TestHTMLParser:
    """Tests for HTMLParser class."""

    def test_parse_html(self, mock_email_generator):
        """Test HTML parsing."""
        parser = HTMLParser()
        generator = mock_email_generator

        json_data = generator.generate_json_attachment()
        html = generator.generate_html_body(json_data)

        result = parser.parse_html(html)

        # Verify basic structure
        assert "date" in result
        assert "consensus_opportunities" in result
        assert "non_consensus_opportunities" in result

    def test_extract_date(self, mock_email_generator):
        """Test date extraction from HTML."""
        parser = HTMLParser()
        from bs4 import BeautifulSoup

        html = "<html><body>2026-01-13</body></html>"
        soup = BeautifulSoup(html, "lxml")

        date = parser._extract_date(soup)

        assert "2026-01-13" in date

    def test_parse_empty_html(self):
        """Test parsing empty HTML."""
        parser = HTMLParser()

        with pytest.raises(DataProcessingError):
            parser.parse_html("")
