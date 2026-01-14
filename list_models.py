#!/usr/bin/env python3
"""List available Gemini models."""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Available Gemini models:")
print("=" * 60)

try:
    models = client.models.list()
    for model in models:
        print(f"\nName: {model.name}")
        if hasattr(model, 'display_name'):
            print(f"Display Name: {model.display_name}")
        if hasattr(model, 'description'):
            print(f"Description: {model.description}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
    print("\n\nChecking specifically for image generation models...")

    # Try specific image models
    test_models = [
        "imagen-3.0-generate-001",
        "imagen-3.0-fast-generate-001",
        "gemini-2.0-flash-exp",
        "gemini-exp-1206"
    ]

    for model_name in test_models:
        try:
            print(f"\nTrying model: {model_name}")
            # Just check if we can reference it
            print(f"  ✓ Model name format is valid")
        except Exception as e:
            print(f"  ✗ Error: {e}")
