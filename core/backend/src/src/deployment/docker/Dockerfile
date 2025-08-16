# ApexAgent Multi-Stage Dockerfile
# This Dockerfile implements a multi-stage build process for ApexAgent
# with separate stages for development, testing, and production

###################
# BASE STAGE
###################
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.5.1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy project files
COPY pyproject.toml poetry.lock* ./

###################
# DEVELOPMENT STAGE
###################
FROM base AS development

# Install development dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev

# Install additional development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Set environment to development
ENV ENVIRONMENT=development

# Expose development ports
EXPOSE 8000 8080 5678

# Command to run development server with hot reload
CMD ["poetry", "run", "python", "-m", "src.main", "--dev"]

###################
# TESTING STAGE
###################
FROM base AS testing

# Install all dependencies including test dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with test

# Copy source code and tests
COPY . .

# Set environment to testing
ENV ENVIRONMENT=testing

# Command to run tests
CMD ["poetry", "run", "pytest"]

###################
# PRODUCTION STAGE
###################
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Set working directory
WORKDIR /app

# Create non-root user
RUN groupadd -g 1000 apexagent && \
    useradd -u 1000 -g apexagent -s /bin/bash -m apexagent

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files from base stage
COPY --from=base /app/poetry.lock /app/pyproject.toml ./

# Install only production dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main --no-dev && \
    pip uninstall -y poetry

# Copy source code
COPY --chown=apexagent:apexagent ./src ./src
COPY --chown=apexagent:apexagent ./alembic.ini ./alembic.ini
COPY --chown=apexagent:apexagent ./alembic ./alembic

# Create necessary directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R apexagent:apexagent /app

# Switch to non-root user
USER apexagent

# Expose production port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Command to run production server
CMD ["python", "-m", "src.main"]
