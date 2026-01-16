#!/bin/bash
# End-to-end test script for GrokViz workflow

set -e

echo "======================================"
echo "GrokViz End-to-End Test"
echo "======================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo ""
echo "Step 1: Checking configuration..."
echo "  - Email server: $EMAIL_SERVER"
echo "  - Telegram chat ID: $TELEGRAM_CHAT_ID"
echo "  - Gemini model: $GEMINI_MODEL"

echo ""
echo "Step 2: Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Step 3: Running main workflow..."
echo "  (This will process any unread emails from $GROK_SENDER_EMAIL)"

python -m src.main

EXIT_CODE=$?

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Test PASSED - Workflow completed successfully"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "⚠️  Test PARTIAL - Some emails failed to process"
else
    echo "❌ Test FAILED - Workflow encountered errors"
fi
echo "======================================"

exit $EXIT_CODE
