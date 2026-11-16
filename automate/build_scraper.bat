@echo off
REM Build script for google-maps-scraper Go binary (Windows)
REM This script downloads and builds the scraper binary for use with the automation

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set BUILD_DIR=%SCRIPT_DIR%google-maps-scraper-build
set REPO_DIR=%BUILD_DIR%\google-maps-scraper
set BINARY_NAME=google-maps-scraper.exe

echo Building google-maps-scraper for Windows...

REM Check if Go is installed
where go >nul 2>nul
if %errorlevel% neq 0 (
    echo Go is not installed. Please install Go 1.21+ first.
    echo Visit: https://golang.org/dl/
    exit /b 1
)

for /f "tokens=3" %%i in ('go version') do set GO_VERSION=%%i
echo Found Go version: %GO_VERSION%

REM Create build directory
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"
cd /d "%BUILD_DIR%"

REM Clone or update repository
if exist "%REPO_DIR%" (
    echo Updating existing repository...
    cd /d "%REPO_DIR%"
    git fetch origin
    git reset --hard origin/main
) else (
    echo Cloning repository...
    git clone https://github.com/gosom/google-maps-scraper.git
    cd /d "%REPO_DIR%"
)

REM Download dependencies
echo Downloading Go dependencies...
go mod download

REM Build binary
echo Building binary...
go build -o %BINARY_NAME% .

REM Verify binary
if exist "%BINARY_NAME%" (
    echo Build successful!
    echo Binary: %REPO_DIR%\%BINARY_NAME%

    REM Copy to automation root
    copy /Y "%BINARY_NAME%" "%SCRIPT_DIR%%BINARY_NAME%"
    echo Copied to: %SCRIPT_DIR%%BINARY_NAME%

    REM Test binary
    echo Testing binary...
    "%BINARY_NAME%" -h 2>&1 | more
) else (
    echo Build failed - binary not found
    exit /b 1
)

echo.
echo =========================================
echo Build completed successfully!
echo =========================================
echo Binary location: %SCRIPT_DIR%%BINARY_NAME%
echo.
echo To use with automation:
echo   1. Ensure binary is in automate/ folder
echo   2. Run: python run.py --full
echo =========================================