#!/usr/bin/env python3
"""Test script to verify Gemini image generation API integration."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.infographic.generator import InfographicGenerator
from tests.mock_email_generator import MockEmailGenerator

def main():
    """Run integration test for Gemini image generation."""
    print("=" * 60)
    print("Gemini Image Generation API Integration Test")
    print("=" * 60)

    # Load environment variables
    load_dotenv()

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image")

    if not gemini_api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment")
        sys.exit(1)

    print(f"\n✓ API Key: {gemini_api_key[:20]}...")
    print(f"✓ Model: {gemini_model}")

    # Create test data
    print("\n" + "-" * 60)
    print("Step 1: Generating mock data...")
    print("-" * 60)

    mock_generator = MockEmailGenerator()
    test_data = mock_generator.generate_json_attachment()

    print(f"✓ Generated mock data with:")
    print(f"  - {len(test_data['consensus_opportunities'])} consensus opportunities")
    print(f"  - {len(test_data['non_consensus_opportunities'])} non-consensus opportunities")
    print(f"  - Date: {test_data['date']}")

    # Initialize infographic generator
    print("\n" + "-" * 60)
    print("Step 2: Initializing Gemini client...")
    print("-" * 60)

    try:
        temp_dir = Path("/Users/taosu/Workspace/grokviz/data/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        generator = InfographicGenerator(
            api_key=gemini_api_key,
            model_name=gemini_model,
            output_dir=temp_dir,
            max_retries=3,
            retry_delay=5
        )
        print("✓ Gemini client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        sys.exit(1)

    # Generate infographic
    print("\n" + "-" * 60)
    print("Step 3: Generating infographic...")
    print("-" * 60)
    print("This may take 30-60 seconds...")

    try:
        image_path = generator.generate(test_data, timeout=120)
        print(f"\n✓ Infographic generated successfully!")
        print(f"  - Saved to: {image_path}")
        print(f"  - File size: {image_path.stat().st_size / 1024:.2f} KB")

        # Verify image
        from PIL import Image
        img = Image.open(image_path)
        width, height = img.size
        print(f"  - Dimensions: {width}x{height}px")

        if width >= 1200 and height >= 1800:
            print("  - ✓ Image meets minimum size requirements (1200x1800)")
        else:
            print(f"  - ⚠️  Warning: Image size {width}x{height} is below recommended 1200x1800")

    except Exception as e:
        print(f"\n❌ Failed to generate infographic: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print(f"\nYou can view the generated infographic at:\n{image_path}")

if __name__ == "__main__":
    main()
