# GrokViz Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Copy cron job configuration
COPY cron/grokviz-cron /etc/cron.d/grokviz-cron

# Create data directories
RUN mkdir -p /app/data/logs /app/data/temp /app/data/archive

# Setup cron job
RUN chmod 0644 /etc/cron.d/grokviz-cron && \
    crontab /etc/cron.d/grokviz-cron && \
    touch /var/log/cron.log

# Make scripts executable
RUN chmod +x /app/scripts/*.sh || true
RUN chmod +x /app/scripts/*.py || true

# Environment variables (defaults, override with .env or docker-compose)
ENV PYTHONUNBUFFERED=1 \
    LOG_LEVEL=INFO \
    DATA_DIR=/app/data \
    TEMP_DIR=/app/data/temp

# Health check
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD /app/scripts/health_check.sh || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting GrokViz cron service..."\n\
echo "Cron schedule: */30 * * * * (every 30 minutes)"\n\
printenv | grep -v "no_proxy" >> /etc/environment\n\
cron && tail -f /var/log/cron.log\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/app/start.sh"]
