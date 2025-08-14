# ApexAgent Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional production dependencies
RUN pip install --no-cache-dir \
    gunicorn \
    prometheus-client \
    psycopg2-binary \
    celery \
    flower

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Create necessary directories
RUN mkdir -p logs data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash apexagent
RUN chown -R apexagent:apexagent /app
USER apexagent

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production startup command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--timeout", "120", "--keepalive", "5", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "--log-level", "info", "src.main:app"]

