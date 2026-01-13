"""JSON data processor for Grok daily reports."""

from typing import Dict, Any, List

from src.utils.errors import DataProcessingError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JSONProcessor:
    """Process and validate JSON data from Grok daily reports."""

    REQUIRED_FIELDS = ["date"]
    OPTIONAL_FIELDS = [
        "consensus_opportunities",
        "non_consensus_opportunities",
        "macro_indicators"
    ]

    def process_attachment(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process JSON attachment data.

        Args:
            json_data: Raw JSON data from attachment

        Returns:
            Normalized and validated data structure

        Raises:
            DataProcessingError: If validation or processing fails
        """
        try:
            logger.info("Processing JSON data")

            # Validate structure
            self.validate_structure(json_data)

            # Normalize data
            normalized_data = self.normalize_data(json_data)

            logger.info("JSON data processed successfully")
            return normalized_data

        except DataProcessingError:
            raise
        except Exception as e:
            raise DataProcessingError(
                f"Unexpected error processing JSON data: {e}",
                context={"error": str(e)}
            )

    def validate_structure(self, json_data: Dict[str, Any]) -> None:
        """
        Validate that JSON data has required fields.

        Args:
            json_data: JSON data to validate

        Raises:
            DataProcessingError: If validation fails
        """
        if not isinstance(json_data, dict):
            raise DataProcessingError(
                "JSON data must be a dictionary",
                context={"type": type(json_data).__name__}
            )

        # Check required fields
        missing_fields = [
            field for field in self.REQUIRED_FIELDS
            if field not in json_data
        ]

        if missing_fields:
            raise DataProcessingError(
                f"Missing required fields in JSON data: {missing_fields}",
                context={"missing_fields": missing_fields}
            )

        # Validate opportunities structure if present
        for opp_field in ["consensus_opportunities", "non_consensus_opportunities"]:
            if opp_field in json_data:
                opportunities = json_data[opp_field]
                if not isinstance(opportunities, list):
                    raise DataProcessingError(
                        f"Field '{opp_field}' must be a list",
                        context={"field": opp_field, "type": type(opportunities).__name__}
                    )

                for idx, opp in enumerate(opportunities):
                    if not isinstance(opp, dict):
                        raise DataProcessingError(
                            f"Opportunity in '{opp_field}' must be a dictionary",
                            context={"field": opp_field, "index": idx}
                        )

        logger.debug("JSON structure validation passed")

    def normalize_data(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize JSON data to standard format.

        Args:
            json_data: Raw JSON data

        Returns:
            Normalized data structure
        """
        normalized = {
            "date": json_data.get("date"),
            "consensus_opportunities": self._normalize_opportunities(
                json_data.get("consensus_opportunities", [])
            ),
            "non_consensus_opportunities": self._normalize_opportunities(
                json_data.get("non_consensus_opportunities", [])
            ),
            "macro_indicators": json_data.get("macro_indicators", {})
        }

        return normalized

    @staticmethod
    def _normalize_opportunities(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize opportunity data.

        Args:
            opportunities: List of opportunity dictionaries

        Returns:
            Normalized opportunities
        """
        normalized = []

        for opp in opportunities:
            normalized_opp = {
                "name": opp.get("name", "Unknown"),
                "logic": opp.get("logic", ""),
                "evidence": opp.get("evidence", ""),
                "heat_score": opp.get("heat_score", 0)
            }
            normalized.append(normalized_opp)

        return normalized

    def extract_summary(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract summary information from processed data.

        Args:
            data: Normalized data

        Returns:
            Dictionary with summary information
        """
        consensus_count = len(data.get("consensus_opportunities", []))
        non_consensus_count = len(data.get("non_consensus_opportunities", []))

        # Get top opportunity from each category
        consensus_top = ""
        if data.get("consensus_opportunities"):
            consensus_top = data["consensus_opportunities"][0].get("name", "")

        non_consensus_top = ""
        if data.get("non_consensus_opportunities"):
            non_consensus_top = data["non_consensus_opportunities"][0].get("name", "")

        return {
            "date": data.get("date", ""),
            "consensus_count": str(consensus_count),
            "non_consensus_count": str(non_consensus_count),
            "consensus_top": consensus_top,
            "non_consensus_top": non_consensus_top
        }
