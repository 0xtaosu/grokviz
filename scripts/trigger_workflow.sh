#!/bin/bash
# Manual workflow trigger script

set -e

echo "========================================================================"
echo "GrokViz Manual Workflow Trigger"
echo "========================================================================"
echo ""

# Check if container is running
if ! docker ps | grep -q grokviz; then
    echo "❌ Error: grokviz container is not running"
    echo "Start it with: docker-compose up -d"
    exit 1
fi

echo "✓ Container is running"
echo ""

# Show options
echo "Choose trigger method:"
echo "  1) Run workflow directly (calls Grok API for real data)"
echo "  2) Run E2E test (bypass Grok API, uses mock data)"
echo ""
read -p "Enter choice (1-2): " choice

case $choice in
    1)
        echo ""
        echo "Running workflow in container..."
        echo "This will call Grok API to generate a real crypto report."
        echo ""
        docker exec -it grokviz python -m src.main
        ;;
    2)
        echo ""
        echo "Running end-to-end test (bypasses Grok API)..."
        echo "This generates mock data → Gemini API → Telegram"
        echo ""
        docker exec -it grokviz python /app/test_workflow_e2e.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================================================"
echo "✅ Workflow execution completed!"
echo "========================================================================"
echo ""
echo "Check results:"
echo "  - Telegram channel: Check for new infographic"
echo "  - Container logs: docker-compose logs grokviz"
echo "  - Application logs: tail -f data/logs/grokviz.log"
echo "  - Generated images: ls -lh data/temp/"
echo ""
