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

### Setup & Installation

```bash
# Clone repository
git clone <repository-url>
cd grokviz

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Local Development

```bash
# Run workflow once
python -m src.main

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Generate and send mock email for testing
python scripts/generate_mock_email.py

# End-to-end test
bash scripts/test_workflow.sh
```

### Docker Deployment

```bash
# Build and start container
docker-compose up -d

# View logs
docker-compose logs -f grokviz
tail -f data/logs/grokviz.log

# Check container health
docker exec grokviz /app/scripts/health_check.sh

# Stop container
docker-compose down

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Debugging

```bash
# Check cron status
docker exec grokviz crontab -l
docker exec grokviz tail /var/log/cron.log

# Manual run inside container
docker exec grokviz python -m src.main

# Interactive shell
docker exec -it grokviz bash
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

### Project Structure

```
grokviz/
├── src/                          # Application source
│   ├── main.py                   # Main workflow (orchestrates all modules)
│   ├── config.py                 # Configuration management (env vars)
│   ├── email_monitor/            # Email module
│   │   ├── client.py            # IMAP client with retry logic
│   │   └── parser.py            # Email parsing & attachment extraction
│   ├── data_processor/           # Data processing module
│   │   ├── json_processor.py    # JSON validation & normalization
│   │   └── html_parser.py       # HTML fallback parser
│   ├── infographic/              # Infographic generation module
│   │   ├── generator.py         # Gemini API integration
│   │   └── prompts.py           # Prompt templates
│   ├── telegram/                 # Telegram module
│   │   └── bot.py               # Telegram bot integration
│   └── utils/                    # Shared utilities
│       ├── logger.py            # Centralized logging
│       └── errors.py            # Custom exceptions
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── mock_email_generator.py  # Mock email generator
│   └── test_*.py                # Unit tests
├── scripts/                      # Helper scripts
│   ├── generate_mock_email.py   # Send test email
│   ├── test_workflow.sh         # E2E test
│   └── health_check.sh          # Health check
├── data/                         # Runtime data (gitignored)
│   ├── logs/                    # Application logs
│   ├── temp/                    # Generated infographics
│   └── archive/                 # Archived emails
├── cron/                         # Cron configuration
│   └── grokviz-cron             # Runs every 30 minutes
├── Dockerfile                    # Container build
├── docker-compose.yml            # Multi-container orchestration
└── requirements.txt              # Python dependencies
```

### Key Design Principles

- **Modular architecture**: Each module is independent and testable
- **Configuration via environment**: No hardcoded credentials
- **Error handling**: Retry logic with exponential backoff
- **Logging**: Comprehensive logging with rotation (10MB, 5 backups)
- **Fallback mechanisms**: JSON → HTML → Skip with logging

## Future Roadmap Context

Understanding planned features helps inform architectural decisions:
- V1.1: Interactive Telegram bot commands (manual trigger, historical queries)
- V1.2: Multiple infographic templates (dark mode, compact layouts)
- V2.0: Multi-source data aggregation beyond Grok
- V2.1: Web interface for archival and search
