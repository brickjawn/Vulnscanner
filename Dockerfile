# Multi-stage build for minimal production image
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    build-base

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    nmap \
    nmap-scripts \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/cache/apk/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN addgroup -g 1000 vulnscanner && \
    adduser -D -s /bin/sh -u 1000 -G vulnscanner vulnscanner

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=vulnscanner:vulnscanner . .

# Create directories for output
RUN mkdir -p /app/reports /app/logs && \
    chown -R vulnscanner:vulnscanner /app

# Create launcher script before switching users
RUN echo '#!/bin/sh\npython /app/main.py "$@"' > /usr/local/bin/vulnscan && \
    chmod +x /usr/local/bin/vulnscan

# Switch to non-root user
USER vulnscanner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["python", "/app/main.py"]
CMD ["--help"]

# Labels for metadata
LABEL maintainer="Security Team" \
      version="2.0" \
      description="VulnScanner - Professional Vulnerability Scanner" \
      org.opencontainers.image.title="VulnScanner" \
      org.opencontainers.image.description="Advanced Penetration Testing Toolkit" \
      org.opencontainers.image.version="2.0" \
      org.opencontainers.image.vendor="Security Research" \
      org.opencontainers.image.licenses="Educational" 