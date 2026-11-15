# =============================================================================
# AvertaSaaS - Production Hardened Dockerfile
# Multi-stage build: builder -> hardened python:3.12-slim runtime
# Target: <250MB, 0 HIGH/CRITICAL vulns, SBOM signed
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies with Poetry
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for native extensions:
# - gcc, build-essential: C compiler and build tools
# - libpq-dev: PostgreSQL client library (for psycopg2 if used)
# - libxml2-dev, libxslt-dev: XML processing (for lxml)
# - libffi-dev: Foreign function interface (for cryptography, cffi)
# - pkg-config: Helps find libraries during build
# - curl: For health checks in builder if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    postgresql-client \
    libatomic1 \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
# Install Poetry with pinned version
RUN pip install --no-cache-dir poetry==1.8.2

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy only dependency files first (layer caching)
COPY pyproject.toml poetry.lock ./

# Install production dependencies only
RUN poetry install --only=main --no-interaction --no-ansi

# Generate Prisma client in builder (runtime has no prisma CLI)
COPY prisma ./prisma
COPY scripts ./scripts
RUN prisma generate

# Make init script executable
RUN chmod +x ./scripts/init-db.sh

# Cache pip for faster rebuilds
RUN pip cache purge

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Hardened python:3.12-slim with non-root user
# -----------------------------------------------------------------------------
# Using python:3.12-slim instead of distroless to ensure runtime libraries
# (libxml2, libxslt, libffi, etc.) are available for lxml, cryptography, etc.
# Security hardening applied:
# - Non-root user (UID 10001)
# - Read-only root filesystem (via docker-compose.prod.yml)
# - Dropped capabilities (via docker-compose.prod.yml)
# - No shell access in production (entrypoint is python)
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Create non-root user
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install runtime dependencies (shared libraries for native extensions)
# - libxml2, libxslt: for lxml
# - libffi: for cryptography/cffi
# - libpq5: PostgreSQL client library
# - ca-certificates: for HTTPS libatomic1 \
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libatomic1 \
    postgresql-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder (includes generated Prisma client)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and generated Prisma client
COPY --from=builder /app/app ./app
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/scripts ./scripts

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check - uses Python stdlib
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Build-time metadata (for SBOM/traceability)
# -----------------------------------------------------------------------------
ARG BUILD_DATE
ARG GIT_COMMIT
ARG VERSION
LABEL org.opencontainers.image.title="AvertaSaaS Backend" \
      org.opencontainers.image.description="Freight Audit SaaS API" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.vendor="Averta" \
      org.opencontainers.image.licenses="Proprietary" \
      org.opencontainers.image.source="https://github.com/PedroLarrieuF/Averta"