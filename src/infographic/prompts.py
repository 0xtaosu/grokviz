"""Prompt templates for Gemini Pro infographic generation."""

import json
from typing import Dict, Any


INFOGRAPHIC_PROMPT = """You are a top-tier information designer who excels at transforming complex data into clear, beautiful, and easy-to-understand infographics.

Your task is to create a stunning infographic for 'Grok Crypto Daily Digest' based on the provided JSON data. The infographic should clearly display two main sections: 'Consensus Opportunities' and 'Non-Consensus Opportunities'.

**Design Requirements:**

1. **Layout & Style:**
   - Hand-drawn doodle style with cute, playful aesthetic
   - Cream-colored background (#FFF8E7 or similar warm off-white)
   - Dimensions: Minimum 1200x1800 pixels (portrait orientation, vertical long image)
   - Organized rectangular areas with rounded corners and thin outlines
   - Flat design with clean, minimalist composition
   - Similar to digital bullet journals or creative financial newsletters

2. **Header Section:**
   - Title: "每日新闻" (Daily News) or "Grok Crypto Daily Digest" (prominent, hand-drawn style typography)
   - Date: Display prominently below title
   - Include a cute banana cartoon mascot character as a visual anchor

3. **Color Scheme:**
   - Use soft MACARON COLORS throughout:
     * Light blue (#B4D7E8 or similar pastel blue)
     * Soft green (#C8E6C9 or similar mint green)
     * Gentle yellow (#FFF9C4 or similar pastel yellow)
     * Lavender purple (#E1BEE7 or similar soft purple)
   - Avoid harsh contrasts; keep everything soft and harmonious

4. **Consensus Opportunities Section:**
   - Use warm macaron tones (soft yellow, peach, light orange)
   - Each opportunity displayed as a rounded rectangle card with thin outline
   - Include:
     * Opportunity name (hand-drawn style font, bold)
     * Core logic (clear, concise text)
     * Key evidence (supporting data)
     * Visual heat indicator using semi-circular dashboard gauges or cute bar charts
   - Arrange opportunities in descending order by heat_score

5. **Non-Consensus Opportunities Section:**
   - Use cool macaron tones (light blue, lavender, mint green)
   - Same rounded card structure as consensus section
   - Clearly distinguish from consensus section with different color palette
   - Include same elements: name, logic, evidence, heat indicator

6. **Visual Elements:**
   - Semi-circular dashboard gauges for metrics
   - Simple line charts with hand-drawn aesthetic
   - Financial K-line charts (candlestick charts) where appropriate
   - Small doodle icons: rockets 🚀, buildings 🏢, coins, charts, etc.
   - Heat scores represented with cute visual indicators (not just numbers)
   - Decorative elements in hand-drawn style

7. **Macro Indicators (if provided):**
   - Display in a compact dashboard section with rounded containers
   - Use semi-circular gauges, mini line charts, or simple data visualizations
   - Keep it cute and informative with doodle-style icons

8. **Typography:**
   - Clear hierarchy: Title > Section Headers > Opportunity Names > Body Text
   - Hand-drawn or rounded fonts that match the doodle aesthetic
   - Ensure good readability despite the playful style

9. **Branding:**
   - Include subtle "Powered by Grok AI" footer in hand-drawn style
   - Small crypto-related doodle icons (Bitcoin, Ethereum symbols, etc.)
   - Banana mascot can appear in multiple places as a recurring character

**Data to Visualize:**

{json_data}

**Important Notes:**
- Prioritize clarity and cuteness without sacrificing readability
- The aesthetic should be clean, cute, and extremely minimalist
- Use the hand-drawn doodle style consistently throughout
- Soft macaron colors create a gentle, approachable feel
- The infographic should feel like a creative financial newsletter or digital planner page
- High resolution output suitable for social media sharing
- Balance playful design with professional information presentation

Please generate a high-quality infographic that meets all these requirements."""


def format_prompt(data: Dict[str, Any]) -> str:
    """
    Format the infographic prompt with actual data.

    Args:
        data: Normalized data from JSON processor

    Returns:
        Formatted prompt string
    """
    # Convert data to formatted JSON string
    json_data = json.dumps(data, indent=2, ensure_ascii=False)

    # Format the prompt
    prompt = INFOGRAPHIC_PROMPT.format(json_data=json_data)

    return prompt


def generate_summary_prompt(data: Dict[str, Any]) -> str:
    """
    Generate a concise text summary prompt for Telegram caption.

    Args:
        data: Normalized data

    Returns:
        Prompt for generating caption text
    """
    json_data = json.dumps(data, indent=2, ensure_ascii=False)

    prompt = f"""Based on this crypto daily report data, generate a concise summary (2-3 sentences) highlighting the most important opportunities:

{json_data}

The summary should:
1. Mention the top 1-2 most significant consensus opportunities
2. Mention the most interesting non-consensus opportunity
3. Be engaging and informative
4. Use professional but accessible language

Keep it under 200 characters."""

    return prompt
