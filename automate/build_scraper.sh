#!/bin/bash
# Build script for google-maps-scraper Go binary
# This script downloads and builds the scraper binary for use with the automation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/google-maps-scraper-build"
REPO_DIR="$BUILD_DIR/google-maps-scraper"
BINARY_NAME="google-maps-scraper"

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $ARCH in
    x86_64) ARCH="amd64" ;;
    arm64|aarch64) ARCH="arm64" ;;
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

echo "Building google-maps-scraper for $OS/$ARCH"

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "Go is not installed. Please install Go 1.21+ first."
    echo "Visit: https://golang.org/dl/"
    exit 1
fi

GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
echo "Found Go version: $GO_VERSION"

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Clone or update repository
if [ -d "$REPO_DIR" ]; then
    echo "Updating existing repository..."
    cd "$REPO_DIR"
    git fetch origin
    git reset --hard origin/main
else
    echo "Cloning repository..."
    git clone https://github.com/gosom/google-maps-scraper.git
    cd "$REPO_DIR"
fi

# Download dependencies
echo "Downloading Go dependencies..."
go mod download

# Build binary
echo "Building binary..."
if [ "$OS" = "windows" ] || [ "$OS" = "mingw"* ] || [ "$OS" = "msys"* ]; then
    BINARY_NAME="${BINARY_NAME}.exe"
    GOOS=windows GOARCH=$ARCH go build -o "$BINARY_NAME" .
else
    GOOS=$OS GOARCH=$ARCH go build -o "$BINARY_NAME" .
fi

# Verify binary
if [ -f "$BINARY_NAME" ]; then
    echo "Build successful!"
    echo "Binary: $REPO_DIR/$BINARY_NAME"

    # Copy to automation root
    cp "$BINARY_NAME" "$SCRIPT_DIR/$BINARY_NAME"
    echo "Copied to: $SCRIPT_DIR/$BINARY_NAME"

    # Test binary
    echo "Testing binary..."
    if [ "$OS" = "windows" ] || [ "$OS" = "mingw"* ] || [ "$OS" = "msys"* ]; then
        "./$BINARY_NAME" -h 2>&1 | head -20
    else
        ./$BINARY_NAME -h 2>&1 | head -20
    fi
else
    echo "Build failed - binary not found"
    exit 1
fi

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo "Binary location: $SCRIPT_DIR/$BINARY_NAME"
echo ""
echo "To use with automation:"
echo "  1. Ensure binary is in automate/ folder"
echo "  2. Run: python run.py --full"
echo "========================================="