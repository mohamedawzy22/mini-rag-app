# FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm

# WORKDIR /app

# # Install additional system dependencies for lxml and other packages
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libavif-dev pkg-config \
#     libjpeg-dev \
#     gcc unzip zip \
#     python3-dev \
#     libxml2-dev \
#     libxslt1-dev \
#     libffi-dev \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# COPY src/requirements.txt .

# RUN uv pip install -r requirements.txt --system

# COPY src/ .

# # Create directory structure for Alembic
# RUN mkdir -p /app/models/db_schemes/minirag/

# COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini

# COPY docker/minirag/entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# ENTRYPOINT ["/entrypoint.sh"]

# # Command to run the application
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# =========================
# Stage 1: Builder
# =========================
FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm AS builder

WORKDIR /app

# System packages required only for building Python dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    libavif-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    pkg-config \
    unzip \
    zip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN uv venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Copy requirements separately for Docker layer caching
COPY src/requirements.txt .

# Install dependencies
RUN uv pip install -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.10-slim-bookworm AS runtime

WORKDIR /app

# Runtime libraries only
RUN apt-get update && apt-get install -y \
    libavif15 \
    libjpeg62-turbo \
    libxml2 \
    libxslt1.1 \
    libffi8 \
    libpq5 \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Make virtual environment the default Python environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source
COPY src/ .

# Alembic directory
RUN mkdir -p /app/models/db_schema/minirag

COPY docker/minirag/alembic.ini \
     /app/models/db_schema/minirag/alembic.ini

# Entrypoint
COPY docker/minirag/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Run as non-root user
RUN useradd \
    --create-home \
    --shell /bin/bash \
    appuser

RUN chown -R appuser:appuser /app /entrypoint.sh

USER appuser

ENTRYPOINT ["/entrypoint.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]