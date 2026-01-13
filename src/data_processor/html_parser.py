"""HTML parser for extracting data from email body as fallback."""

import re
from typing import Dict, Any, List

from bs4 import BeautifulSoup

from src.utils.errors import DataProcessingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HTMLParser:
    """Parse HTML email body to extract Grok daily report data."""

    def parse_html(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML content to extract structured data.

        This is a fallback method when JSON attachment is not available.

        Args:
            html_content: HTML email body

        Returns:
            Structured data in same format as JSON processor

        Raises:
            DataProcessingError: If parsing fails
        """
        try:
            logger.info("Parsing HTML content (fallback mode)")

            if not html_content:
                raise DataProcessingError("HTML content is empty")

            soup = BeautifulSoup(html_content, "lxml")

            # Extract date (look for date patterns)
            date = self._extract_date(soup)

            # Extract opportunities
            consensus_opportunities = self._extract_opportunities(
                soup, "consensus", ["共识机会", "consensus opportunities"]
            )
            non_consensus_opportunities = self._extract_opportunities(
                soup, "non-consensus", ["非共识机会", "non-consensus opportunities"]
            )

            # Extract macro indicators (if present)
            macro_indicators = self._extract_macro_indicators(soup)

            data = {
                "date": date,
                "consensus_opportunities": consensus_opportunities,
                "non_consensus_opportunities": non_consensus_opportunities,
                "macro_indicators": macro_indicators
            }

            logger.info(
                f"HTML parsing completed: {len(consensus_opportunities)} consensus, "
                f"{len(non_consensus_opportunities)} non-consensus opportunities found"
            )

            return data

        except Exception as e:
            raise DataProcessingError(
                f"Failed to parse HTML content: {e}",
                context={"error": str(e)}
            )

    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract date from HTML content."""
        # Look for common date patterns
        text = soup.get_text()

        # Pattern: YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
        date_pattern = r'(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})'
        match = re.search(date_pattern, text)
        if match:
            date_str = match.group(1)
            # Normalize to YYYY-MM-DD format
            date_str = date_str.replace("/", "-").replace(".", "-")
            logger.debug(f"Extracted date: {date_str}")
            return date_str

        # If no date found, use current date as fallback
        from datetime import datetime
        fallback_date = datetime.now().strftime("%Y-%m-%d")
        logger.warning(f"Could not extract date from HTML, using current date: {fallback_date}")
        return fallback_date

    def _extract_opportunities(
        self,
        soup: BeautifulSoup,
        opp_type: str,
        section_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract opportunities from HTML.

        Args:
            soup: BeautifulSoup object
            opp_type: Type of opportunity ("consensus" or "non-consensus")
            section_keywords: Keywords to identify the section

        Returns:
            List of opportunity dictionaries
        """
        opportunities = []

        # Find section by keywords
        section = None
        for keyword in section_keywords:
            # Look for headers or strong text containing the keyword
            headers = soup.find_all(["h1", "h2", "h3", "h4", "strong", "b"])
            for header in headers:
                if keyword.lower() in header.get_text().lower():
                    section = header
                    break
            if section:
                break

        if not section:
            logger.warning(f"Could not find {opp_type} section in HTML")
            return opportunities

        # Extract opportunities from section
        # Look for list items or paragraphs after the section header
        current = section.find_next()
        while current and len(opportunities) < 10:  # Limit to 10 opportunities
            # Stop if we hit another major section
            if current.name in ["h1", "h2", "h3"]:
                break

            text = current.get_text(strip=True)
            if text and len(text) > 20:  # Skip very short text
                # Try to parse opportunity from text
                opp = self._parse_opportunity_text(text)
                if opp:
                    opportunities.append(opp)

            current = current.find_next()

        return opportunities

    def _parse_opportunity_text(self, text: str) -> Dict[str, Any]:
        """
        Parse opportunity from text.

        Tries to extract name, logic, and evidence from text.

        Args:
            text: Text containing opportunity information

        Returns:
            Opportunity dictionary or None if parsing fails
        """
        # Simple heuristic: split by common delimiters
        # Format might be: "Name: Logic. Evidence"
        # or just a paragraph describing the opportunity

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return None

        # First line is likely the name
        name = lines[0][:100]  # Limit length

        # Rest is logic and evidence
        logic = ""
        evidence = ""

        if len(lines) > 1:
            logic = lines[1][:200] if len(lines) > 1 else ""
            evidence = lines[2][:200] if len(lines) > 2 else ""
        else:
            # Try to split first line
            parts = text.split(".", 1)
            if len(parts) > 1:
                name = parts[0][:100]
                logic = parts[1][:200]

        # Default heat score (can't determine from HTML)
        heat_score = 50

        return {
            "name": name,
            "logic": logic,
            "evidence": evidence,
            "heat_score": heat_score
        }

    def _extract_macro_indicators(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract macro indicators from HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of macro indicators
        """
        # This is a simplified extraction
        # In practice, would need to parse specific HTML structure
        indicators = {}

        text = soup.get_text()

        # Look for common indicators with regex patterns
        # BTC dominance
        btc_dom_match = re.search(r'btc[^\d]*dominance[^\d]*([\d.]+)', text, re.IGNORECASE)
        if btc_dom_match:
            indicators["btc_dominance"] = float(btc_dom_match.group(1))

        # Fear & Greed Index
        fear_greed_match = re.search(r'fear[^\d]*greed[^\d]*index[^\d]*([\d]+)', text, re.IGNORECASE)
        if fear_greed_match:
            indicators["fear_greed_index"] = int(fear_greed_match.group(1))

        # Market cap
        market_cap_match = re.search(r'market[^\d]*cap[^\d]*([\d.]+)\s*([TBM])', text, re.IGNORECASE)
        if market_cap_match:
            value = market_cap_match.group(1)
            unit = market_cap_match.group(2).upper()
            indicators["total_market_cap"] = f"{value}{unit}"

        logger.debug(f"Extracted macro indicators: {indicators}")
        return indicators
