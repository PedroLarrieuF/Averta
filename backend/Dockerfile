# =============================================================================
# AvertaSaaS - Production Hardened Dockerfile
# Multi-stage build: builder -> distroless runtime
# Target: <200MB, 0 HIGH/CRITICAL vulns, SBOM signed
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies with Poetry
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry with pinned version
RUN pip install --no-cache-dir poetry==1.8.2

# Configure poetry
RUN poetry config virtualenvs.create false

# Copy only dependency files first (layer caching)
COPY pyproject.toml poetry.lock ./

# Install production dependencies only
RUN poetry install --only=main --no-interaction --no-ansi

# Generate Prisma client in builder (distroless has no prisma CLI)
COPY prisma ./prisma
COPY scripts ./scripts
RUN prisma generate

# Make init script executable
RUN chmod +x ./scripts/init-db.sh

# Cache pip for faster rebuilds
RUN pip cache purge

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Distroless base for minimal attack surface
# -----------------------------------------------------------------------------
# Using gcr.io/distroless/python3-debian12:nonroot
# - No shell, no package manager, no unnecessary binaries
# - Runs as non-root user (UID 65532)
# - Includes Python 3.12 + standard library + ca-certificates
# -----------------------------------------------------------------------------
FROM gcr.io/distroless/python3-debian12:nonroot AS runtime

WORKDIR /app

# Copy installed Python packages from builder (includes generated Prisma client)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and generated Prisma client
COPY --from=builder /app/app ./app
COPY --from=builder /app/prisma ./prisma
COPY --from=builder /app/scripts ./scripts

# Expose port
EXPOSE 8000

# Health check - uses Python stdlib (no curl in distroless)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Run application
# Distroless uses ENTRYPOINT ["python", "-m"] format
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