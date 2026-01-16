# GrokViz

**Automated Grok Crypto Daily Report to Infographic Pipeline**

GrokViz is an intelligent automation system that transforms Grok crypto daily reports into beautiful infographics and delivers them via Telegram. Built with Python, powered by Gemini Pro AI, and designed for 24/7 automated operation.

## Features

- 📧 **Automated Email Monitoring**: IMAP-based email fetching with smart filtering
- 🔄 **Dual Data Processing**: JSON attachment parsing with HTML fallback
- 🎨 **AI-Powered Infographics**: Gemini Pro API generates stunning visualizations
- 📱 **Telegram Integration**: Instant delivery to your Telegram channel/chat
- 🐳 **Docker Deployment**: Containerized with cron-based scheduling
- 🔒 **Secure Configuration**: Environment-based credential management
- 📊 **Comprehensive Logging**: Detailed logs with rotation
- ⚡ **High Performance**: < 3 minutes end-to-end processing time

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Grok Email (Daily Report)                              │
│  ├── JSON Attachment (Primary)                          │
│  └── HTML Body (Fallback)                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  GrokViz Workflow                                        │
│  ├── 1. Email Monitor (IMAP)                            │
│  ├── 2. Data Processor (JSON/HTML)                      │
│  ├── 3. Infographic Generator (Gemini Pro)              │
│  └── 4. Telegram Bot (Delivery)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Telegram Channel/Chat                                   │
│  📊 Infographic + Caption                                │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Email account with IMAP access (Gmail recommended)
- [Gemini API key](https://ai.google.dev/)
- [Telegram bot token](https://core.telegram.org/bots#creating-a-new-bot)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd grokviz
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required configuration:

```bash
# Email Configuration
EMAIL_SERVER=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # Use app-specific password
GROK_SENDER_EMAIL=grok@example.com

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-pro

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id  # Can be user ID or channel ID
```

### Getting Credentials

#### Gmail App Password

1. Enable 2-factor authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app password for "Mail"
4. Use this as `EMAIL_PASSWORD`

#### Gemini API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create a new API key
3. Use this as `GEMINI_API_KEY`

#### Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command to create a bot
3. Copy the bot token
4. For channel posting, add bot as administrator
5. Use channel ID or chat ID as `TELEGRAM_CHAT_ID`

To get chat ID:
```bash
# Send a message to your bot, then:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# Look for "chat":{"id": YOUR_CHAT_ID}
```

## Usage

### Local Development

**Run the workflow once:**

```bash
python -m src.main
```

**Run tests:**

```bash
pytest tests/ -v
```

**Test with mock email:**

```bash
python scripts/generate_mock_email.py
```

**End-to-end test:**

```bash
bash scripts/test_workflow.sh
```

### Docker Deployment

**Build and start:**

```bash
docker-compose up -d
```

**View logs:**

```bash
docker-compose logs -f grokviz
```

**Check status:**

```bash
docker-compose ps
docker exec grokviz /app/scripts/health_check.sh
```

**Stop:**

```bash
docker-compose down
```

## Configuration

### Environment Variables

All configuration is done via environment variables (`.env` file or Docker environment):

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_SERVER` | IMAP server address | Required |
| `EMAIL_PORT` | IMAP port (SSL) | 993 |
| `EMAIL_USERNAME` | Email account username | Required |
| `EMAIL_PASSWORD` | Email account password | Required |
| `GROK_SENDER_EMAIL` | Filter emails by sender | Required |
| `GEMINI_API_KEY` | Gemini API key | Required |
| `GEMINI_MODEL` | Gemini model name | gemini-1.5-pro |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID | Required |
| `LOG_LEVEL` | Logging level | INFO |
| `DATA_DIR` | Data directory | /app/data |
| `TEMP_DIR` | Temporary files directory | /app/data/temp |
| `ARCHIVE_EMAILS` | Archive processed emails | true |
| `PROCESSING_TIMEOUT` | Max processing time (seconds) | 180 |
| `MAX_RETRIES` | Retry attempts for operations | 3 |
| `RETRY_DELAY` | Base retry delay (seconds) | 5 |

### Cron Schedule

Default schedule: **Every 30 minutes**

To modify, edit `cron/grokviz-cron`:

```cron
# Run every hour instead
0 * * * * cd /app && /usr/local/bin/python -m src.main >> /var/log/cron.log 2>&1

# Run twice daily (9 AM and 9 PM)
0 9,21 * * * cd /app && /usr/local/bin/python -m src.main >> /var/log/cron.log 2>&1
```

## Project Structure

```
grokviz/
├── src/                          # Application source code
│   ├── main.py                   # Main workflow orchestration
│   ├── config.py                 # Configuration management
│   ├── email_monitor/            # Email fetching and parsing
│   ├── data_processor/           # JSON/HTML data processing
│   ├── infographic/              # Gemini infographic generation
│   ├── telegram/                 # Telegram bot integration
│   └── utils/                    # Logging and error handling
├── tests/                        # Test suite
│   ├── conftest.py               # Pytest fixtures
│   ├── mock_email_generator.py   # Mock email generator
│   └── test_*.py                 # Unit tests
├── scripts/                      # Utility scripts
│   ├── generate_mock_email.py    # Send test email
│   ├── test_workflow.sh          # E2E test
│   └── health_check.sh           # Container health check
├── data/                         # Runtime data (not in git)
│   ├── logs/                     # Application logs
│   ├── temp/                     # Generated infographics
│   └── archive/                  # Archived emails
├── cron/                         # Cron job definitions
├── Dockerfile                    # Container build definition
├── docker-compose.yml            # Multi-container orchestration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_email_monitor.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
pylint src/

# Type checking
mypy src/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes in appropriate module
3. Add tests in `tests/`
4. Update documentation
5. Submit pull request

## Monitoring & Logs

### Log Files

Logs are written to `data/logs/grokviz.log` with automatic rotation (10MB max, 5 backups).

**Log format:**
```
[2026-01-13 10:30:15] [INFO] [grokviz.main] GrokViz workflow started
[2026-01-13 10:30:16] [INFO] [email_monitor.client] Connected to IMAP server
[2026-01-13 10:30:17] [INFO] [infographic.generator] Infographic generated in 28.3s
[2026-01-13 10:30:19] [INFO] [telegram.bot] Sent to Telegram: message_id=12345
```

### View Logs

**Docker:**
```bash
docker-compose logs -f grokviz
tail -f data/logs/grokviz.log
```

**Local:**
```bash
tail -f data/logs/grokviz.log
```

### Health Monitoring

**Docker health check:**
```bash
docker exec grokviz /app/scripts/health_check.sh
```

**Check cron status:**
```bash
docker exec grokviz crontab -l
docker exec grokviz tail /var/log/cron.log
```

## Troubleshooting

### Email Connection Issues

**Problem:** Cannot connect to IMAP server

**Solutions:**
- Verify EMAIL_SERVER and EMAIL_PORT are correct
- For Gmail: Enable "Less secure app access" or use app password
- Check firewall/network settings
- Verify credentials with: `openssl s_client -connect imap.gmail.com:993`

### Gemini API Errors

**Problem:** Infographic generation fails

**Solutions:**
- Verify GEMINI_API_KEY is valid
- Check API quota limits
- Try different model: `GEMINI_MODEL=gemini-pro`
- Check Gemini API status

### Telegram Send Failures

**Problem:** Cannot send to Telegram

**Solutions:**
- Verify bot token is correct
- Ensure bot is added to channel as administrator
- Check chat ID format (channel IDs start with -100)
- Test bot: `curl https://api.telegram.org/bot<TOKEN>/getMe`

### Docker Issues

**Problem:** Container fails to start

**Solutions:**
- Check logs: `docker-compose logs grokviz`
- Verify .env file exists and is configured
- Check permissions on data/ directories
- Rebuild: `docker-compose build --no-cache`

## Performance

### Benchmarks

Based on typical Grok daily report:

| Operation | Target | Typical |
|-----------|--------|---------|
| Email fetch | < 10s | 3-5s |
| Data processing | < 5s | 1-2s |
| Infographic generation | < 120s | 30-60s |
| Telegram send | < 10s | 2-5s |
| **Total end-to-end** | **< 3 min** | **40-80s** |

### Success Rate

Target: **> 99%**

Factors affecting success:
- Email server availability
- Gemini API quota and availability
- Telegram API availability
- Network connectivity

## Security

### Best Practices

- ✅ Never commit `.env` file to git
- ✅ Use app-specific passwords for email
- ✅ Rotate API keys regularly
- ✅ Restrict Telegram bot permissions
- ✅ Keep Docker images updated
- ✅ Monitor logs for suspicious activity
- ✅ Use encrypted connections (IMAP SSL, HTTPS)

### Sensitive Data

The following are NEVER logged:
- Email passwords
- API keys
- Bot tokens

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Create an issue](<repository-url>/issues)
- Documentation: See [CLAUDE.md](CLAUDE.md) for development guide

## Acknowledgments

- Powered by [Gemini Pro](https://ai.google.dev/) for AI infographic generation
- Built with [python-telegram-bot](https://python-telegram-bot.org/)
- Inspired by the Grok crypto daily reports

---

**Made with ❤️ for the crypto community**
