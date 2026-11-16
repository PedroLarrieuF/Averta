#!/usr/bin/env python3
"""
Download pre-built google-maps-scraper binary from GitHub releases.
Alternative to building from source.
"""

import os
import sys
import platform
import subprocess
import urllib.request
import json
import zipfile
import tarfile
from pathlib import Path
from typing import Optional


def get_platform_info() -> tuple:
    """Get platform and architecture info."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture
    if machine in ('x86_64', 'amd64'):
        arch = 'amd64'
    elif machine in ('arm64', 'aarch64'):
        arch = 'arm64'
    elif machine in ('i386', 'i686'):
        arch = '386'
    else:
        arch = machine

    # Normalize OS
    if system == 'darwin':
        os_name = 'darwin'
    elif system == 'windows':
        os_name = 'windows'
    elif system == 'linux':
        os_name = 'linux'
    else:
        os_name = system

    return os_name, arch


def get_latest_release() -> dict:
    """Get latest release info from GitHub API."""
    api_url = "https://api.github.com/repos/gosom/google-maps-scraper/releases/latest"

    try:
        req = urllib.request.Request(api_url)
        req.add_header('Accept', 'application/vnd.github.v3+json')

        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching release info: {e}")
        return {}


def find_asset(release: dict, os_name: str, arch: str) -> Optional[dict]:
    """Find matching asset for platform."""
    # Expected asset naming patterns
    patterns = [
        f"google-maps-scraper_{release['tag_name']}_{os_name}_{arch}.zip",
        f"google-maps-scraper_{release['tag_name']}_{os_name}_{arch}.tar.gz",
        f"google-maps-scraper_{os_name}_{arch}.zip",
        f"google-maps-scraper_{os_name}_{arch}.tar.gz",
    ]

    for asset in release.get('assets', []):
        asset_name = asset['name']
        for pattern in patterns:
            if asset_name == pattern or asset_name.startswith(pattern.replace('.zip', '').replace('.tar.gz', '')):
                return asset

    # Fallback: try to match by OS and arch in name
    for asset in release.get('assets', []):
        name_lower = asset['name'].lower()
        if os_name in name_lower and arch in name_lower:
            return asset

    return None


def download_and_extract(asset: dict, output_dir: Path, binary_name: str) -> Optional[Path]:
    """Download and extract binary."""
    url = asset['browser_download_url']
    filename = asset['name']

    print(f"Downloading {filename} from {url}")

    try:
        # Download
        local_file = output_dir / filename
        urllib.request.urlretrieve(url, local_file)
        print(f"Downloaded to {local_file}")

        # Extract
        if filename.endswith('.zip'):
            with zipfile.ZipFile(local_file, 'r') as zf:
                zf.extractall(output_dir)
        elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
            with tarfile.open(local_file, 'r:gz') as tf:
                tf.extractall(output_dir)
        else:
            print(f"Unknown archive format: {filename}")
            return None

        # Find binary
        for extracted in output_dir.rglob(binary_name):
            if extracted.is_file():
                # Make executable on Unix
                if os.name != 'nt':
                    extracted.chmod(0o755)
                print(f"Found binary: {extracted}")
                return extracted

        print(f"Binary {binary_name} not found in extracted files")
        return None

    except Exception as e:
        print(f"Error downloading/extracting: {e}")
        return None


def main():
    """Main entry point."""
    print("Google Maps Scraper Binary Downloader")
    print("=" * 50)

    # Get platform info
    os_name, arch = get_platform_info()
    print(f"Platform: {os_name}/{arch}")

    # Determine binary name
    binary_name = "google-maps-scraper.exe" if os_name == "windows" else "google-maps-scraper"

    # Get latest release
    print("Fetching latest release...")
    release = get_latest_release()

    if not release:
        print("Failed to get release info")
        sys.exit(1)

    print(f"Latest release: {release.get('tag_name', 'unknown')}")

    # Find matching asset
    asset = find_asset(release, os_name, arch)

    if not asset:
        print(f"No matching asset found for {os_name}/{arch}")
        print("Available assets:")
        for a in release.get('assets', []):
            print(f"  - {a['name']}")
        sys.exit(1)

    print(f"Found asset: {asset['name']}")

    # Download and extract
    output_dir = Path.cwd()
    binary_path = download_and_extract(asset, output_dir, binary_name)

    if binary_path:
        # Copy to current directory with standard name
        target = output_dir / binary_name
        if binary_path != target:
            import shutil
            shutil.copy2(binary_path, target)
            if os.name != 'nt':
                target.chmod(0o755)

        print(f"\nSuccess! Binary available at: {target}")
        print(f"You can now run: python run.py --full")
    else:
        print("\nFailed to download binary")
        sys.exit(1)


if __name__ == "__main__":
    main()