"""xAI Grok API client."""
import json
import time
from typing import Dict, Any
import requests
from ..utils.logger import get_logger
from ..utils.errors import GrokAPIError

logger = get_logger(__name__)


class GrokClient:
    """xAI Grok API client with OpenAI-compatible format."""

    def __init__(
        self,
        api_key: str,
        model: str = "grok-4",
        base_url: str = "https://api.x.ai/v1",
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """Initialize Grok API client.

        Args:
            api_key: xAI API key
            model: Model name (default: grok-beta)
            base_url: API base URL
            max_retries: Maximum number of retries
            retry_delay: Initial retry delay in seconds
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def generate_report(self, prompt: str, timeout: int = 120) -> Dict[str, Any]:
        """Call Grok API to generate crypto analysis report.

        Args:
            prompt: Analysis prompt
            timeout: Request timeout in seconds

        Returns:
            Structured JSON data from Grok

        Raises:
            GrokAPIError: If API call fails after retries
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Grok API (attempt {attempt + 1}/{self.max_retries})...")

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )

                # Handle different status codes
                if response.status_code == 401:
                    raise GrokAPIError("Invalid API key (401 Unauthorized)")

                if response.status_code == 429:
                    logger.warning("Rate limit hit (429), retrying with backoff...")
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise GrokAPIError("Rate limit exceeded after retries")

                if response.status_code >= 500:
                    logger.warning(f"Server error ({response.status_code}), retrying...")
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise GrokAPIError(f"Server error after retries: {response.status_code}")

                response.raise_for_status()

                # Parse response
                data = response.json()

                if "choices" not in data or len(data["choices"]) == 0:
                    raise GrokAPIError("No choices in API response")

                content = data["choices"][0]["message"]["content"]

                # Parse JSON from content
                try:
                    result = json.loads(content)
                    logger.info("Grok API call successful")
                    return result
                except json.JSONDecodeError as e:
                    raise GrokAPIError(f"Failed to parse JSON response: {e}")

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise GrokAPIError("Request timeout after retries")

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                raise GrokAPIError(f"Request failed after retries: {e}")

        raise GrokAPIError("Max retries exceeded")
