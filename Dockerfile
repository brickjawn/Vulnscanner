# VulnScanner - Dockerized Web Vulnerability Scanner
FROM python:3.11-slim

LABEL maintainer="VulnScanner" \
      version="2.0" \
      description="Web Application Vulnerability Scanner"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scanner code
COPY scanner/ ./scanner/
COPY main.py .

# Run as non-root user
RUN useradd -m scanner && chown -R scanner:scanner /app
USER scanner

ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
