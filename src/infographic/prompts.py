"""Prompt templates for Gemini Pro infographic generation."""

import json
from typing import Dict, Any


INFOGRAPHIC_PROMPT = """You are a top-tier information designer who excels at transforming complex data into clear, beautiful, and easy-to-understand infographics.

Your task is to create a stunning infographic for 'Grok Crypto Daily Digest' based on the provided JSON data. The infographic should clearly display two main sections: 'Consensus Opportunities' and 'Non-Consensus Opportunities'.

**Design Requirements:**

1. **Layout & Style:**
   - Modern, minimalist tech aesthetic with clean lines and professional appearance
   - Overall color scheme: Dark mode with vibrant accent colors
   - Dimensions: Minimum 1200x1800 pixels (portrait orientation)
   - Use a gradient background or subtle texture for visual interest

2. **Header Section:**
   - Title: "Grok Crypto Daily Digest" (prominent, eye-catching typography)
   - Date: Display prominently below title
   - Subtitle: "AI-Powered Crypto Intelligence" or similar tagline

3. **Consensus Opportunities Section:**
   - Use WARM COLORS (orange #FF6B35, gold #F7931A, amber #FFA500)
   - Each opportunity displayed as a card or tile
   - Include:
     * Opportunity name (bold, large font)
     * Core logic (clear, concise text)
     * Key evidence (supporting data)
     * Visual heat indicator (bar chart, thermometer, or heat dots showing the heat_score)
   - Arrange opportunities in descending order by heat_score

4. **Non-Consensus Opportunities Section:**
   - Use COOL COLORS (blue #4A90E2, purple #9B59B6, cyan #00D4FF)
   - Same card/tile structure as consensus section
   - Clearly distinguish from consensus section with different color scheme
   - Include same elements: name, logic, evidence, heat indicator

5. **Visual Elements:**
   - Heat scores should be represented visually (not just numbers)
   - Use icons or symbols for different opportunity types where appropriate
   - Include charts or graphs if macro indicators are present
   - Add subtle connecting lines or dividers between sections

6. **Macro Indicators (if provided):**
   - Display in a compact dashboard-style section at bottom
   - Use small charts, gauges, or data visualizations
   - Keep it concise but informative

7. **Typography:**
   - Clear hierarchy: Title > Section Headers > Opportunity Names > Body Text
   - Use professional, readable fonts (Sans-serif recommended)
   - Ensure good contrast for readability

8. **Branding:**
   - Include subtle "Powered by Grok AI" footer
   - Can include small crypto-related icons (Bitcoin logo, etc.) tastefully

**Data to Visualize:**

{json_data}

**Important Notes:**
- Prioritize clarity and readability over decorative elements
- Ensure the infographic is easy to scan and understand in 30 seconds
- Make the heat scores immediately visible through visual indicators
- Use color psychology: warm colors suggest activity/consensus, cool colors suggest opportunity/potential
- The final output should be professional enough to share on social media

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
