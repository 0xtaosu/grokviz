# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GrokViz is an automated workflow system that processes Grok crypto daily reports and generates infographics for Telegram distribution. The system:

1. Monitors email for Grok daily reports via IMAP
2. Extracts JSON data from email attachments (or parses HTML content as fallback)
3. Generates infographics using Gemini Pro API
4. Pushes results to Telegram channels/users

## Technical Stack

- **Language**: Python 3.11
- **Email Processing**: `imaplib`, `email` (standard library)
- **AI Integration**: `google-generativeai` SDK for Gemini Pro
- **Telegram**: `python-telegram-bot` framework
- **Deployment**: Docker containerization
- **Scheduling**: `cron` for task automation

## Core Architecture

The system follows a pipeline architecture with these key modules:

### 1. Email Subscription & Parsing Module
- Connects to email server via IMAP (with IDLE support for real-time monitoring)
- Parses HTML emails and extracts attachments
- Handles connection errors with auto-reconnect

### 2. Data Extraction & Processing Module
- **Primary**: Extracts JSON file from email attachments
- **Fallback**: Parses email HTML body using regex/DOM parsing when JSON is missing
- Extracts three core sections:
  - Information collection and processing logic
  - Consensus opportunities and non-consensus opportunities
  - Market macro and on-chain indicators
- Validates and normalizes data into standard format

### 3. Infographic Generation Module
- Calls Gemini Pro API with structured prompts
- Generates PNG images (minimum 1200x1800px resolution)
- Uses distinct color schemes: warm colors (orange/gold) for consensus opportunities, cool colors (blue/purple) for non-consensus

### 4. Telegram Push Module
- Sends generated infographics via Telegram Bot API
- Includes caption with title, date, summary, and hashtags (#GrokDaily #CryptoInsights)
- Implements retry logic and failure alerts

## Development Commands

When the codebase is implemented, commands will likely include:

```bash
# Setup
pip install -r requirements.txt

# Run locally
python main.py

# Run tests
pytest

# Docker
docker build -t grokviz .
docker run -d --env-file .env grokviz
```

## Critical Requirements

### Security
- All credentials (email passwords, API keys, Telegram tokens) MUST be managed via environment variables or key management services
- Never hardcode sensitive information

### Performance Targets
- End-to-end latency: < 3 minutes (average)
- P95 latency: < 5 minutes
- Processing success rate: > 99%

### Error Handling
- Implement comprehensive logging for all modules
- Alert on critical failures (via email or backup Telegram channel)
- Auto-reconnect for IMAP connection drops
- Retry logic for Telegram sending failures

## Gemini Pro Prompt Template

The infographic generation prompt should include:

1. **Role**: "You are a top-tier information designer who excels at transforming complex data into clear, beautiful, and easy-to-understand infographics."

2. **Task**: "Based on the following JSON data, create an infographic for 'Grok Crypto Daily'. The chart should clearly display two sections: 'Consensus Opportunities' and 'Non-Consensus Opportunities'."

3. **Layout & Style**:
   - Modern, minimalist tech aesthetic
   - Header with title 'Grok Crypto Daily Digest' and date
   - Consensus opportunities: warm colors (orange/gold)
   - Non-consensus opportunities: cool colors (blue/purple)
   - Each opportunity includes: name, core logic, key evidence
   - Visual indicators (bar charts/heat points) for importance scores

4. **Data Input**: Inject the structured JSON data

## Code Organization

Follow modular design principles:
- Separate configuration from code
- Clear module boundaries for each pipeline stage
- Comprehensive documentation and comments
- Unit tests for data parsing and transformation logic

## Future Roadmap Context

Understanding planned features helps inform architectural decisions:
- V1.1: Interactive Telegram bot commands (manual trigger, historical queries)
- V1.2: Multiple infographic templates (dark mode, compact layouts)
- V2.0: Multi-source data aggregation beyond Grok
- V2.1: Web interface for archival and search
