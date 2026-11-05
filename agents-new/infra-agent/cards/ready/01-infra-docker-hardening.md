# Card #01 - Docker Production Hardening

## Overview
Harden the Docker images and build pipeline for production deployment. Current multi-stage build works but needs security hardening, supply chain security, and production optimizations.

## Priority: HIGH
## Estimate: M (Medium)

## Current State
- `backend/Dockerfile` exists with multi-stage build (builder + runtime)
- `docker-compose.yml` for local development (6 services)
- Python 3.11-slim base images
- Non-root user (appuser) configured

## Required Work

### 1. Base Image Hardening
- [ ] Switch runtime stage to distroless: `gcr.io/distroless/python3-debian12:nonroot`
- [ ] Remove shell, package manager, and unnecessary binaries
- [ ] Verify all Python dependencies work on distroless (no glibc issues)

### 2. Security Scanning (CI Integration)
- [ ] Add Trivy scan to `.github/workflows/build.yml`
- [ ] Fail build on HIGH/CRITICAL vulnerabilities
- [ ] Add Trivy database update step

### 3. SBOM Generation
- [ ] Add Syft to generate SPDX SBOM in build pipeline
- [ ] Upload SBOM as build artifact
- [ ] Sign SBOM with cosign (keyless)

### 4. Multi-Architecture Builds
- [ ] Configure buildx for linux/amd64, linux/arm64
- [ ] Push multi-arch manifests to registry
- [ ] Test arm64 compatibility (CI runners)

### 5. Docker Content Trust
- [ ] Enable DOCKER_CONTENT_TRUST=1
- [ ] Configure cosign keyless signing (GitHub OIDC)
- [ ] Verify signatures in deploy pipeline

### 6. Layer Optimization
- [ ] Reorder COPY commands: deps first, then source
- [ ] Combine RUN commands where possible
- [ ] Use `--mount=type=cache` for pip cache
- [ ] Target final image size < 200MB

### 7. Health Checks
- [ ] Add HEALTHCHECK to Dockerfile (curl /health)
- [ ] Configure interval=30s, timeout=10s, retries=3
- [ ] Update docker-compose healthchecks to match

### 8. Production Compose File
- [ ] Create `docker-compose.prod.yml` with:
  - Resource limits (CPU, memory)
  - Restart policies (unless-stopped)
  - Logging driver (json-file + max-size)
  - Read-only root filesystem
  - Drop capabilities (ALL)
  - Security opt (no-new-privileges)

## Acceptance Criteria
- [ ] Trivy scan passes with 0 HIGH/CRITICAL vulns
- [ ] SBOM generated and signed for each build
- [ ] Multi-arch images available on registry
- [ ] Production compose file validated
- [ ] Image size reduced by ≥30% vs current
- [ ] Health checks pass in staging

## Files to Modify
- `backend/Dockerfile`
- `backend/docker-compose.prod.yml` (new)
- `.github/workflows/build.yml`
- `.github/workflows/ci.yml` (add security scan)

## Dependencies
- None (can start immediately)

## Notes
- Test distroless compatibility locally first: `docker run --rm gcr.io/distroless/python3-debian12 python -c "import prisma; print('OK')"`
- Use `docker scout` as alternative to Trivy if preferred
- Consider `cgr.dev/chainguard/python` as alternative distroless