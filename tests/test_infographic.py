"""Tests for infographic generation module."""

import pytest
from src.infographic.prompts import format_prompt, INFOGRAPHIC_PROMPT


class TestPrompts:
    """Tests for prompt generation."""

    def test_format_prompt(self, mock_json_data):
        """Test prompt formatting with data."""
        prompt = format_prompt(mock_json_data)

        # Verify prompt contains data
        assert "consensus_opportunities" in prompt.lower()
        assert "non_consensus_opportunities" in prompt.lower()
        assert mock_json_data["date"] in prompt

    def test_prompt_template_structure(self):
        """Test prompt template has required elements."""
        # Verify key sections exist
        assert "information designer" in INFOGRAPHIC_PROMPT.lower()
        assert "consensus opportunities" in INFOGRAPHIC_PROMPT.lower()
        assert "non-consensus opportunities" in INFOGRAPHIC_PROMPT.lower()
        assert ("warm" in INFOGRAPHIC_PROMPT.lower() or "macaron" in INFOGRAPHIC_PROMPT.lower())
        assert ("cool" in INFOGRAPHIC_PROMPT.lower() or "macaron" in INFOGRAPHIC_PROMPT.lower())


# Note: Full integration test for InfographicGenerator requires Gemini API key
# and will be tested in integration tests
