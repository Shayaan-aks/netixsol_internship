# ── Build Stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ── Runtime Stage (Minimal Image) ────────────────────────────────────────────
FROM python:3.11-slim

# Security: Create non-root user
RUN groupadd -r agentuser && useradd -r -g agentuser agentuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/agentuser/.local

# Copy application source
COPY src/ /app/src/

# Set ownership
RUN chown -R agentuser:agentuser /app /home/agentuser/.local

# Switch to non-root user
USER agentuser

# Ensure local bin is on PATH
ENV PATH=/home/agentuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# ── Environment Variables (injected at runtime via docker run -e or .env) ────
# GEMINI_API_KEY — Required. Passed via docker-compose env_file or -e flag.
# DAY5_AGENT_PATH — Optional. Override agent path if different in container.

EXPOSE 8000

# Docker health check — polls /health every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.deployment.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
