<#
.SYNOPSIS
    Build script for google-maps-scraper Go binary (PowerShell version)

.DESCRIPTION
    This script downloads and builds the google-maps-scraper Go binary for use with the automation.
    It clones the repository, builds the binary, and copies it to the automation root directory.

.NOTES
    Requires Go 1.21+ to be installed and in PATH.
#>

param(
    [string]$OutputPath = ".\google-maps-scraper.exe"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BuildDir = Join-Path $ScriptDir "google-maps-scraper-build"
$RepoDir = Join-Path $BuildDir "google-maps-scraper"
$BinaryName = "google-maps-scraper.exe"

Write-Host "Building google-maps-scraper for Windows..." -ForegroundColor Cyan

# Check if Go is installed
try {
    $GoVersion = (go version).Split(' ')[2]
    Write-Host "Found Go version: $GoVersion" -ForegroundColor Green
} catch {
    Write-Error "Go is not installed. Please install Go 1.21+ first."
    Write-Host "Visit: https://golang.org/dl/" -ForegroundColor Yellow
    exit 1
}

# Create build directory
if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

# Clone or update repository
if (Test-Path $RepoDir) {
    Write-Host "Updating existing repository..." -ForegroundColor Yellow
    Set-Location $RepoDir
    git fetch origin
    git reset --hard origin/main
} else {
    Write-Host "Cloning repository..." -ForegroundColor Yellow
    git clone https://github.com/gosom/google-maps-scraper.git $RepoDir
    Set-Location $RepoDir
}

# Download dependencies
Write-Host "Downloading Go dependencies..." -ForegroundColor Yellow
go mod download

# Build binary
Write-Host "Building binary..." -ForegroundColor Yellow
go build -o $BinaryName .

# Verify binary
if (Test-Path $BinaryName) {
    Write-Host "Build successful!" -ForegroundColor Green
    Write-Host "Binary: $RepoDir\$BinaryName" -ForegroundColor Cyan

    # Copy to automation root
    Copy-Item -Path $BinaryName -Destination $OutputPath -Force
    Write-Host "Copied to: $OutputPath" -ForegroundColor Cyan

    # Test binary
    Write-Host "Testing binary..." -ForegroundColor Yellow
    & $BinaryName -h 2>&1 | Select-Object -First 20
} else {
    Write-Error "Build failed - binary not found"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Binary location: $OutputPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use with automation:" -ForegroundColor Yellow
Write-Host "  1. Ensure binary is in automate/ folder" -ForegroundColor White
Write-Host "  2. Run: python run.py --full" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan