"""Infographic generator using Gemini Pro API."""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import io

from google import genai
from google.genai import types
from PIL import Image

from src.infographic.prompts import format_prompt
from src.utils.errors import InfographicGenerationError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InfographicGenerator:
    """Generate infographics using Gemini Pro API."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3-pro-image-preview",
        output_dir: Optional[Path] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize infographic generator.

        Args:
            api_key: Gemini API key
            model_name: Gemini model to use (gemini-2.5-flash-image or gemini-3-pro-image-preview)
            output_dir: Directory to save generated images
            max_retries: Maximum retry attempts for API calls
            retry_delay: Base delay between retries in seconds
        """
        self.api_key = api_key
        self.model_name = model_name
        self.output_dir = output_dir or Path("/app/data/temp")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Initialize Gemini client
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized Gemini client with model: {self.model_name}")
        except Exception as e:
            raise InfographicGenerationError(
                f"Failed to initialize Gemini client: {e}",
                context={"model": self.model_name, "error": str(e)}
            )

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        data: Dict[str, Any],
        timeout: int = 60
    ) -> Path:
        """
        Generate infographic from data.

        Args:
            data: Normalized data from JSON processor
            timeout: Timeout for API call in seconds

        Returns:
            Path to generated infographic image

        Raises:
            InfographicGenerationError: If generation fails
        """
        start_time = time.time()

        try:
            logger.info("Generating infographic via Gemini API")

            # Format prompt with data
            prompt = format_prompt(data)

            # Generate image with retry logic
            image_data = self._call_gemini_api_with_retry(prompt, timeout)

            # Save image
            date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grok_daily_{date_str}_{timestamp}.png"
            image_path = self._save_image(image_data, filename)

            generation_time = time.time() - start_time
            logger.info(
                f"Infographic generated successfully in {generation_time:.2f}s: {image_path}",
                extra={"generation_time_ms": int(generation_time * 1000), "filename": filename}
            )

            return image_path

        except InfographicGenerationError:
            raise
        except Exception as e:
            raise InfographicGenerationError(
                f"Unexpected error during infographic generation: {e}",
                context={"error": str(e)}
            )

    def _call_gemini_api_with_retry(self, prompt: str, timeout: int) -> bytes:
        """
        Call Gemini API with retry logic for image generation.

        Args:
            prompt: Formatted prompt
            timeout: Timeout in seconds

        Returns:
            Image data as bytes

        Raises:
            InfographicGenerationError: If all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Gemini API call attempt {attempt + 1}/{self.max_retries}")

                # Use generate_content for image generation models like gemini-2.5-flash-image
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                # Extract image from response
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]

                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Check if this part contains inline data (image)
                            if hasattr(part, 'inline_data') and part.inline_data:
                                # Get image data from inline_data
                                image_data = part.inline_data.data
                                mime_type = part.inline_data.mime_type

                                logger.info(f"Successfully generated image via Gemini API (type: {mime_type})")

                                # Convert to PNG if needed
                                if mime_type.startswith('image/'):
                                    img_byte_arr = io.BytesIO(image_data)
                                    img = Image.open(img_byte_arr)

                                    # Convert to PNG
                                    output = io.BytesIO()
                                    img.save(output, format='PNG', optimize=True, quality=95)
                                    output.seek(0)

                                    return output.getvalue()
                                else:
                                    return image_data

                # If no image found in response
                raise InfographicGenerationError(
                    "No image data found in Gemini response",
                    context={"response": str(response)[:500]}
                )

            except Exception as e:
                last_error = e
                if attempt == self.max_retries - 1:
                    break

                delay = self.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Gemini API call failed (attempt {attempt + 1}): {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)

        raise InfographicGenerationError(
            f"Failed to generate infographic after {self.max_retries} attempts: {last_error}",
            context={"attempts": self.max_retries, "error": str(last_error)}
        )

    def _save_image(self, image_data: bytes, filename: str) -> Path:
        """
        Save image data to file.

        Args:
            image_data: Image bytes
            filename: Output filename

        Returns:
            Path to saved image

        Raises:
            InfographicGenerationError: If saving fails
        """
        try:
            output_path = self.output_dir / filename

            with open(output_path, "wb") as f:
                f.write(image_data)

            # Verify image
            img = Image.open(output_path)
            width, height = img.size

            logger.info(
                f"Image saved: {output_path} ({width}x{height})",
                extra={"width": width, "height": height, "size_kb": len(image_data) // 1024}
            )

            return output_path

        except Exception as e:
            raise InfographicGenerationError(
                f"Failed to save image: {e}",
                context={"filename": filename, "error": str(e)}
            )
