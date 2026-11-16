#!/usr/bin/env python3
"""
Simple entry point for Averta Lead Generation Automation.

Usage:
    # Pipeline
    python run.py                              # Run full pipeline
    python run.py --generate-queries           # Only generate queries
    python run.py --scrape                     # Only run scraper
    python run.py --qualify                    # Only qualify leads
    python run.py --export                     # Only export results
    python run.py --continuous                 # Run continuously
    python run.py --full --priorities 1 2      # Run with specific priorities
    python run.py --full --max-queries 100     # Limit queries for testing

    # WhatsApp Business
    python run.py --whatsapp-campaign          # Run WhatsApp campaign (dry run)
    python run.py --whatsapp-campaign --execute # Actually send messages
    python run.py --whatsapp-test --lead-id LEAD_123  # Send test message
    python run.py --whatsapp-stats             # Show campaign stats
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main import main

if __name__ == "__main__":
    main()