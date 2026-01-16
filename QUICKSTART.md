# GrokViz Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Clone and Install (1 min)

```bash
git clone <your-repo-url>
cd grokviz
pip install -r requirements.txt
```

### Step 2: Configure Environment (2 min)

```bash
cp .env.example .env
```

Edit `.env` and fill in these required fields:

```bash
# Your email (Gmail recommended)
EMAIL_SERVER=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password  # See below for Gmail setup

# Who sends the Grok reports
GROK_SENDER_EMAIL=grok@example.com

# Get from: https://ai.google.dev/
GEMINI_API_KEY=your-gemini-key-here

# Create bot: https://t.me/botfather
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id  # Your user ID or channel ID
```

#### Quick Gmail Setup

1. Enable 2FA on Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Use that as `EMAIL_PASSWORD`

#### Quick Telegram Setup

1. Message @BotFather, use `/newbot`
2. Copy the token
3. For chat ID, send any message to your bot, then:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getUpdates
   # Look for "chat":{"id": YOUR_ID}
   ```

### Step 3: Test (2 min)

**Option A: Use Mock Email (Recommended for first test)**

```bash
# Generate and send a mock Grok email to your inbox
python scripts/generate_mock_email.py

# Run the workflow to process it
python -m src.main
```

**Option B: Wait for Real Email**

Just run the workflow when you receive a Grok email:

```bash
python -m src.main
```

### Step 4: Deploy with Docker (Optional)

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f grokviz

# Health check
docker exec grokviz /app/scripts/health_check.sh
```

The cron job will run every 30 minutes automatically.

## ✅ Success Checklist

After running, you should see:

1. ✅ Logs in `data/logs/grokviz.log`
2. ✅ Generated infographic in `data/temp/`
3. ✅ Message received in your Telegram chat
4. ✅ Email marked as read in your inbox

## 🔧 Troubleshooting

### "Cannot connect to IMAP server"
- Check `EMAIL_SERVER` and `EMAIL_PORT`
- For Gmail, use app password, not regular password
- Test connection: `openssl s_client -connect imap.gmail.com:993`

### "Gemini API error"
- Verify `GEMINI_API_KEY` is correct
- Check quota at https://ai.google.dev/

### "Telegram send failed"
- Verify bot token: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Ensure chat ID is correct (channels start with -100)

### "No emails found"
- Check `GROK_SENDER_EMAIL` matches actual sender
- Verify there are unread emails from that sender
- Use mock email generator for testing

## 📊 Monitor

```bash
# View logs
tail -f data/logs/grokviz.log

# Docker logs
docker-compose logs -f grokviz

# Check what emails are processed
ls -lh data/temp/
```

## 🎯 Next Steps

1. **Customize cron schedule**: Edit `cron/grokviz-cron`
2. **Enable archiving**: Set `ARCHIVE_EMAILS=true` in `.env`
3. **Run tests**: `pytest tests/ -v`
4. **Read full docs**: See `README.md`

## 💡 Tips

- Test with mock emails first before waiting for real Grok reports
- Check logs frequently during initial setup
- Monitor Gemini API usage and quotas
- Keep backups of `.env` file (but don't commit it!)

---

Need help? Check `README.md` for detailed documentation.
