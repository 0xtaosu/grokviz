"""Infographic generator using Gemini Pro API."""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import io

import google.generativeai as genai
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
        model_name: str = "gemini-1.5-pro",
        output_dir: Optional[Path] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """
        Initialize infographic generator.

        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
            output_dir: Directory to save generated images
            max_retries: Maximum retry attempts for API calls
            retry_delay: Base delay between retries in seconds
        """
        self.api_key = api_key
        self.model_name = model_name
        self.output_dir = output_dir or Path("/app/data/temp")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model
        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            raise InfographicGenerationError(
                f"Failed to initialize Gemini model: {e}",
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
        Call Gemini API with retry logic.

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

                # Note: Gemini API may not directly support image generation in the same way
                # This is a placeholder - actual implementation depends on Gemini's capabilities
                # For MVP, we'll use text generation and convert to image, or use Gemini's
                # multimodal capabilities if available

                # Generate response
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.4,
                        "max_output_tokens": 2048,
                    }
                )

                # For MVP, since Gemini may not directly generate images,
                # we'll create a simple text-based infographic as fallback
                # In production, integrate with Gemini's image generation capabilities
                # or use another service like DALL-E

                # Extract text from response (handle multi-part responses)
                try:
                    response_text = response.text
                except Exception:
                    # Handle multi-part responses
                    response_text = ""
                    if hasattr(response, 'parts'):
                        for part in response.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text'):
                                        response_text += part.text

                # This is a temporary solution - generate a simple image
                image_data = self._create_text_based_infographic(
                    response_text if response_text else "Generated infographic",
                    prompt
                )

                return image_data

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

    def _create_text_based_infographic(self, text_response: str, original_prompt: str) -> bytes:
        """
        Create a text-based infographic as fallback.

        This is a temporary solution for MVP. In production, integrate with
        Gemini's actual image generation capabilities or use a dedicated
        image generation service.

        Args:
            text_response: Text response from Gemini
            original_prompt: Original prompt with data

        Returns:
            PNG image data as bytes
        """
        try:
            from PIL import Image, ImageDraw, ImageFont

            # Create a simple infographic image
            width, height = 1200, 1800
            background_color = "#1a1a2e"
            text_color = "#ffffff"

            # Create image
            img = Image.new("RGB", (width, height), background_color)
            draw = ImageDraw.Draw(img)

            # Try to use a nice font, fallback to default
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                body_font = ImageFont.load_default()

            # Draw header
            y_offset = 50
            draw.text((width // 2, y_offset), "Grok Crypto Daily Digest", fill="#FFD700",
                     font=title_font, anchor="mt")

            y_offset += 100

            # Parse data from prompt (this is simplified)
            draw.text((100, y_offset), "AI-Powered Crypto Intelligence", fill=text_color,
                     font=body_font)

            y_offset += 80

            # Add placeholder text
            placeholder_text = """
            🔥 Consensus Opportunities
            📊 Market Intelligence Report

            This is a simplified MVP infographic.
            For full visual design, integrate with
            Gemini's image generation API or use
            DALL-E / Midjourney.

            Data processed successfully.
            Check logs for details.
            """

            for line in placeholder_text.strip().split("\n"):
                draw.text((100, y_offset), line.strip(), fill=text_color, font=body_font)
                y_offset += 40

            # Save to bytes
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG', optimize=True, quality=95)
            img_byte_arr.seek(0)

            logger.warning(
                "Using simplified text-based infographic. "
                "For production, integrate proper image generation."
            )

            return img_byte_arr.getvalue()

        except Exception as e:
            raise InfographicGenerationError(
                f"Failed to create fallback infographic: {e}",
                context={"error": str(e)}
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
