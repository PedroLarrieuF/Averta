#!/usr/bin/env bash
# fetch_secrets.sh - Fetch secrets from AWS Secrets Manager for local development
# Usage: ./scripts/fetch_secrets.sh [staging|production] [--output .env.local]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${1:-staging}"
OUTPUT_FILE="${2:-.env.local}"
SECRET_PREFIX="averta"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}Error: Environment must be 'staging' or 'production'${NC}"
    echo "Usage: $0 [staging|production] [--output .env.local]"
    exit 1
fi

echo -e "${BLUE}Fetching secrets for ${ENVIRONMENT} environment...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found. Please install it first.${NC}"
    echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq not found. Please install it first.${NC}"
    echo "Visit: https://stedolan.github.io/jq/download/"
    exit 1
fi

# Verify AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured or invalid.${NC}"
    echo "Run: aws configure"
    exit 1
fi

# Secret keys to fetch
SECRET_KEYS=("database" "redis" "minio" "jwt" "sendgrid" "app")

# Start building .env.local content
cat > "$OUTPUT_FILE" <<EOF
# Averta SaaS - Local Development Environment
# Generated from AWS Secrets Manager (${ENVIRONMENT})
# DO NOT COMMIT THIS FILE - Add to .gitignore
# Generated at: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

EOF

SECRETS_FOUND=0

for KEY in "${SECRET_KEYS[@]}"; do
    SECRET_NAME="${SECRET_PREFIX}/${ENVIRONMENT}/${KEY}"

    echo -e "${YELLOW}Fetching ${SECRET_NAME}...${NC}"

    SECRET_VALUE=$(aws secretsmanager get-secret-value \
        --secret-id "$SECRET_NAME" \
        --region "$AWS_REGION" \
        --query 'SecretString' \
        --output text 2>/dev/null || echo "")

    if [[ -n "$SECRET_VALUE" && "$SECRET_VALUE" != "null" ]]; then
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
        echo -e "${GREEN}  ✓ Found${NC}"

        # Parse JSON and export as KEY=VALUE pairs
        echo "$SECRET_VALUE" | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' | while IFS= read -r line; do
            echo "$line" >> "$OUTPUT_FILE"
        done
        echo "" >> "$OUTPUT_FILE"
    else
        echo -e "${YELLOW}  ✗ Not found (using defaults)${NC}"
    fi
done

# Add derived values
if grep -q "DATABASE_URL=" "$OUTPUT_FILE" 2>/dev/null; then
    echo -e "${GREEN}Database URL found in secrets${NC}"
else
    echo -e "${YELLOW}Database URL not in secrets, using local default${NC}"
    cat >> "$OUTPUT_FILE" <<EOF
# Database (local defaults)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/averta
DATABASE_READ_REPLICA_URL=
DATABASE_CONNECT_TIMEOUT=10
DATABASE_POOL_SIZE=20
DATABASE_POOL_TIMEOUT=10

EOF
fi

if ! grep -q "REDIS_URL=" "$OUTPUT_FILE" 2>/dev/null; then
    cat >> "$OUTPUT_FILE" <<EOF
# Redis (local defaults)
REDIS_URL=redis://localhost:6379/0

EOF
fi

if ! grep -q "JWT_SECRET_KEY=" "$OUTPUT_FILE" 2>/dev/null; then
    cat >> "$OUTPUT_FILE" <<EOF
# JWT (generate with: openssl rand -base64 32)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars-long-here
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-min-32-chars-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

EOF
fi

if ! grep -q "S3_ENDPOINT=" "$OUTPUT_FILE" 2>/dev/null; then
    cat >> "$OUTPUT_FILE" <<EOF
# S3/MinIO (local defaults)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=averta-documents
S3_REGION=us-east-1
S3_PUBLIC_URL=http://localhost:9000

EOF
fi

if ! grep -q "SENDGRID_API_KEY=" "$OUTPUT_FILE" 2>/dev/null; then
    cat >> "$OUTPUT_FILE" <<EOF
# Email
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@averta.com
SENDGRID_FROM_NAME="Averta Auditoria"

EOF
fi

# Add standard app config
cat >> "$OUTPUT_FILE" <<EOF
# Application
APP_NAME="Averta SaaS"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development
API_PREFIX="/api/v1"

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000

# Support email
SUPPORT_EMAIL=suporte@averta.com

# Success fee percentage
SUCCESS_FEE_PERCENTAGE=20.0

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_AUTH_REQUESTS=10
RATE_LIMIT_UPLOAD_REQUESTS=5
RATE_LIMIT_API_REQUESTS=100
RATE_LIMIT_REPORTS_REQUESTS=20
RATE_LIMIT_DISCREPANCIES_REQUESTS=50
RATE_LIMIT_CONTESTS_REQUESTS=30

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# File upload
MAX_FILE_SIZE=52428800
ALLOWED_MIME_TYPES=["application/xml", "text/xml", "application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]

EOF

echo -e "${GREEN}Successfully fetched ${SECRETS_FOUND} secrets from AWS Secrets Manager${NC}"
echo -e "${BLUE}Output written to: ${OUTPUT_FILE}${NC}"
echo ""
echo -e "${YELLOW}Note: This file contains sensitive data. Do not commit to version control.${NC}"
echo -e "${YELLOW}Add ${OUTPUT_FILE} to your .gitignore if not already present.${NC}"