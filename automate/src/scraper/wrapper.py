"""Wrapper for google-maps-scraper Go binary."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import os
import subprocess
import json
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
from datetime import datetime
import requests

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id
from storage.models import ScrapedLead

logger = get_logger(__name__)


@dataclass
class ScraperResult:
    """Result of a scraping job."""
    success: bool
    query: str
    results: List[Dict[str, Any]]
    output_file: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    results_count: int = 0


class GoogleMapsScraperWrapper:
    """Wrapper for google-maps-scraper."""

    def __init__(self, config: Optional[Dict] = None):
        self.settings = get_settings()
        self.config = config or {}
        self.binary_path = self._find_binary()
        self.execution_mode = self.settings.scraper_execution_mode

        # REST API settings
        self.rest_api_url = self.settings.scraper_rest_api_base_url
        self.rest_api_timeout = self.settings.scraper_rest_api_timeout_seconds

        logger.info(f"Scraper wrapper initialized - Mode: {self.execution_mode}, Binary: {self.binary_path}")

    def _find_binary(self) -> Optional[str]:
        """Find the google-maps-scraper binary."""
        # Check configured path
        configured = self.settings.scraper_binary_path
        if configured and Path(configured).exists():
            return str(Path(configured).resolve())

        # Check common locations
        possible_paths = [
            "./google-maps-scraper",
            "./google-maps-scraper.exe",
            "../google-maps-scraper",
            "../google-maps-scraper.exe",
            "/usr/local/bin/google-maps-scraper",
            "/opt/google-maps-scraper/google-maps-scraper",
            os.path.expanduser("~/google-maps-scraper/google-maps-scraper"),
        ]

        for path in possible_paths:
            p = Path(path)
            if p.exists() and (p.is_file() and os.access(p, os.X_OK) or p.suffix == '.exe'):
                return str(p.resolve())

        # Check if in PATH
        which_result = shutil.which("google-maps-scraper")
        if which_result:
            return which_result

        logger.warning("google-maps-scraper binary not found. Will attempt to download or use REST API.")
        return None

    def _build_command(self, query_file: str, output_file: str, extra_args: List[str] = None) -> List[str]:
        """Build command for scraper binary."""
        if not self.binary_path:
            raise RuntimeError("Scraper binary not found. Please build or download it first.")

        cmd = [
            self.binary_path,
            "-input", query_file,
            "-results", output_file,
            "-depth", str(self.settings.scraper_params_depth),
            "-c", str(self.settings.scraper_params_concurrency),
            "-exit-on-inactivity", self.settings.scraper_params_exit_on_inactivity,
        ]

        if self.settings.scraper_params_fast_mode:
            cmd.append("-fast-mode")

        if self.settings.scraper_params_extract_emails:
            cmd.append("-email")

        if self.settings.scraper_params_extra_reviews:
            cmd.extend(["-extra-reviews", "-json"])

        if self.settings.scraper_output_format == "json":
            cmd.append("-json")

        if self.settings.scraper_params_grid_cell_km:
            cmd.extend(["-grid-cell", str(self.settings.scraper_params_grid_cell_km)])

        if extra_args:
            cmd.extend(extra_args)

        return cmd

    def scrape_queries(self, queries: List[str], output_dir: str) -> List[ScraperResult]:
        """Scrape multiple queries."""
        results = []

        # Create query file
        query_file = Path(output_dir) / f"queries_{generate_id()}.txt"
        query_file.parent.mkdir(parents=True, exist_ok=True)

        with open(query_file, 'w', encoding='utf-8') as f:
            for query in queries:
                f.write(f"{query}\n")

        logger.info(f"Created query file with {len(queries)} queries: {query_file}")

        # Process in batches
        batch_size = self.settings.scraper_limits_max_queries_per_run
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            batch_file = Path(output_dir) / f"batch_{i//batch_size}_{generate_id()}.txt"

            with open(batch_file, 'w', encoding='utf-8') as f:
                for query in batch:
                    f.write(f"{query}\n")

            output_file = Path(output_dir) / f"results_{i//batch_size}_{generate_id()}.json"

            result = self._run_scraper_batch(batch_file, output_file)
            result.query = f"batch_{i//batch_size}"
            results.append(result)

            # Rate limiting
            if i + batch_size < len(queries):
                time.sleep(2)

        # Cleanup batch files
        for batch_file in Path(output_dir).glob("batch_*.txt"):
            try:
                batch_file.unlink()
            except:
                pass

        return results

    def _run_scraper_batch(self, query_file: Path, output_file: Path) -> ScraperResult:
        """Run scraper on a batch of queries."""
        start_time = time.time()

        if self.execution_mode == "binary":
            return self._run_binary(query_file, output_file, start_time)
        elif self.execution_mode == "rest-api":
            return self._run_rest_api(query_file, output_file, start_time)
        elif self.execution_mode == "docker":
            return self._run_docker(query_file, output_file, start_time)
        else:
            raise ValueError(f"Unknown execution mode: {self.execution_mode}")

    def _run_binary(self, query_file: Path, output_file: Path, start_time: float) -> ScraperResult:
        """Run scraper binary directly."""
        try:
            cmd = self._build_command(str(query_file), str(output_file))
            logger.debug(f"Running scraper command: {' '.join(cmd)}")

            # Run with timeout
            timeout = self.settings.scraper_timeout_seconds
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=query_file.parent
            )

            duration = time.time() - start_time

            if process.returncode != 0:
                error_msg = process.stderr or process.stdout or "Unknown error"
                logger.error(f"Scraper failed with code {process.returncode}: {error_msg}")
                return ScraperResult(
                    success=False,
                    query=str(query_file),
                    results=[],
                    error=error_msg,
                    duration_seconds=duration
                )

            # Parse results
            results = self._parse_results(output_file)

            logger.info(f"Scraper completed in {duration:.1f}s - Found {len(results)} results")

            return ScraperResult(
                success=True,
                query=str(query_file),
                results=results,
                output_file=str(output_file),
                duration_seconds=duration,
                results_count=len(results)
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            logger.error(f"Scraper timeout after {duration:.1f}s")
            return ScraperResult(
                success=False,
                query=str(query_file),
                results=[],
                error=f"Timeout after {duration:.1f}s",
                duration_seconds=duration
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Scraper error: {e}")
            return ScraperResult(
                success=False,
                query=str(query_file),
                results=[],
                error=str(e),
                duration_seconds=duration
            )

    def _run_rest_api(self, query_file: Path, output_file: Path, start_time: float) -> ScraperResult:
        """Run scraper via REST API."""
        try:
            # Read queries
            with open(query_file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]

            # Submit job via REST API
            job_data = {
                "queries": queries,
                "options": {
                    "depth": self.settings.scraper_params_depth,
                    "concurrency": self.settings.scraper_params_concurrency,
                    "fast_mode": self.settings.scraper_params_fast_mode,
                    "extract_emails": self.settings.scraper_params_extract_emails,
                    "output_format": self.settings.scraper_output_format,
                }
            }

            # Submit job
            response = requests.post(
                f"{self.rest_api_url}/api/v1/jobs",
                json=job_data,
                timeout=self.rest_api_timeout
            )
            response.raise_for_status()
            job = response.json()
            job_id = job.get("id")

            if not job_id:
                raise ValueError("No job ID returned from API")

            logger.info(f"Submitted scraping job {job_id} with {len(queries)} queries")

            # Poll for completion
            while True:
                response = requests.get(
                    f"{self.rest_api_url}/api/v1/jobs/{job_id}",
                    timeout=self.rest_api_timeout
                )
                response.raise_for_status()
                job_status = response.json()

                status = job_status.get("status")
                if status == "completed":
                    break
                elif status == "failed":
                    raise RuntimeError(f"Job failed: {job_status.get('error')}")

                time.sleep(5)

            # Download results
            response = requests.get(
                f"{self.rest_api_url}/api/v1/jobs/{job_id}/results",
                timeout=self.rest_api_timeout
            )
            response.raise_for_status()

            # Save results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)

            duration = time.time() - start_time
            results = self._parse_results(output_file)

            logger.info(f"REST API job completed in {duration:.1f}s - Found {len(results)} results")

            return ScraperResult(
                success=True,
                query=str(query_file),
                results=results,
                output_file=str(output_file),
                duration_seconds=duration,
                results_count=len(results)
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"REST API scraper error: {e}")
            return ScraperResult(
                success=False,
                query=str(query_file),
                results=[],
                error=str(e),
                duration_seconds=duration
            )

    def _run_docker(self, query_file: Path, output_file: Path, start_time: float) -> ScraperResult:
        """Run scraper via Docker."""
        try:
            # This would require Docker to be installed and running
            # For now, fall back to binary
            logger.warning("Docker mode not fully implemented, falling back to binary")
            return self._run_binary(query_file, output_file, start_time)
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Docker scraper error: {e}")
            return ScraperResult(
                success=False,
                query=str(query_file),
                results=[],
                error=str(e),
                duration_seconds=duration
            )

    def _parse_results(self, output_file: Path) -> List[Dict[str, Any]]:
        """Parse scraper output file."""
        if not output_file.exists():
            logger.warning(f"Output file not found: {output_file}")
            return []

        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                return []

            # Try JSON first
            if self.settings.scraper_output_format == "json" or content.startswith('[') or content.startswith('{'):
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'results' in data:
                        return data['results']
                    else:
                        return [data]
                except json.JSONDecodeError:
                    # Try parsing as JSONL (one JSON per line)
                    results = []
                    for line in content.split('\n'):
                        line = line.strip()
                        if line:
                            try:
                                results.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                    return results

            # Try CSV
            else:
                import csv
                results = []
                with open(output_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        results.append(row)
                return results

        except Exception as e:
            logger.error(f"Error parsing results: {e}")
            return []

    def convert_to_scraped_leads(self, results: List[Dict], source_query: str) -> List[ScrapedLead]:
        """Convert scraper results to ScrapedLead objects."""
        leads = []

        for result in results:
            try:
                lead = ScrapedLead(
                    source_query=source_query,
                    scraped_at=datetime.utcnow(),

                    # Basic info
                    place_id=result.get('place_id') or result.get('id'),
                    name=result.get('name') or result.get('title'),
                    trade_name=result.get('trade_name') or result.get('name'),

                    # Address
                    address=result.get('address') or result.get('full_address'),
                    street=result.get('street'),
                    number=result.get('number') or result.get('street_number'),
                    complement=result.get('complement'),
                    neighborhood=result.get('neighborhood') or result.get('district'),
                    city=result.get('city') or result.get('address_city'),
                    state=result.get('state') or result.get('address_state'),
                    postal_code=result.get('postal_code') or result.get('zip_code'),
                    country=result.get('country', 'Brasil'),
                    latitude=result.get('latitude') or result.get('lat'),
                    longitude=result.get('longitude') or result.get('lng'),

                    # Contact
                    phone=result.get('phone') or result.get('telephone'),
                    phone_verified=bool(result.get('phone_verified') or result.get('phone_validated')),
                    whatsapp=result.get('whatsapp') or result.get('whatsapp_number'),
                    whatsapp_verified=bool(result.get('whatsapp_verified')),
                    email=result.get('email'),
                    email_verified=bool(result.get('email_verified')),
                    website=result.get('website') or result.get('url'),
                    website_verified=bool(result.get('website_verified')),
                    linkedin=result.get('linkedin') or result.get('linkedin_url'),
                    linkedin_verified=bool(result.get('linkedin_verified')),

                    # Business info
                    rating=result.get('rating'),
                    reviews_count=result.get('reviews_count') or result.get('review_count'),
                    price_level=result.get('price_level'),
                    categories=result.get('categories') or result.get('types') or [],
                    description=result.get('description'),

                    # Hours
                    opening_hours=result.get('opening_hours') or result.get('hours'),
                    permanently_closed=bool(result.get('permanently_closed')),
                    temporarily_closed=bool(result.get('temporarily_closed')),

                    # Additional
                    photos=result.get('photos') or result.get('images') or [],
                    reviews=result.get('reviews') or [],
                    emails_from_website=result.get('emails_from_website') or result.get('emails') or [],
                    social_media=result.get('social_media') or {},

                    # Raw data
                    raw_data=result
                )

                leads.append(lead)

            except Exception as e:
                logger.warning(f"Error converting result to ScrapedLead: {e}")
                continue

        return leads


def download_scraper_binary(platform: str = "windows", arch: str = "amd64") -> Optional[str]:
    """Download pre-built scraper binary from GitHub releases."""
    import urllib.request
    import tarfile
    import zipfile

    try:
        # Get latest release
        api_url = "https://api.github.com/repos/gosom/google-maps-scraper/releases/latest"
        response = urllib.request.urlopen(api_url)
        release = json.loads(response.read())

        # Find asset for platform
        asset_name = None
        if platform == "windows":
            asset_name = f"google-maps-scraper_{release['tag_name']}_windows_{arch}.zip"
        elif platform == "linux":
            asset_name = f"google-maps-scraper_{release['tag_name']}_linux_{arch}.tar.gz"
        elif platform == "darwin":
            asset_name = f"google-maps-scraper_{release['tag_name']}_darwin_{arch}.tar.gz"

        if not asset_name:
            logger.error(f"No asset found for platform {platform}")
            return None

        # Find download URL
        download_url = None
        for asset in release.get('assets', []):
            if asset['name'] == asset_name:
                download_url = asset['browser_download_url']
                break

        if not download_url:
            logger.error(f"Asset {asset_name} not found in release")
            return None

        # Download
        logger.info(f"Downloading {asset_name} from {download_url}")
        local_file = Path.cwd() / asset_name
        urllib.request.urlretrieve(download_url, local_file)

        # Extract
        extract_dir = Path.cwd() / "google-maps-scraper"
        extract_dir.mkdir(exist_ok=True)

        if asset_name.endswith('.zip'):
            with zipfile.ZipFile(local_file, 'r') as zf:
                zf.extractall(extract_dir)
        else:
            with tarfile.open(local_file, 'r:gz') as tf:
                tf.extractall(extract_dir)

        # Find binary
        binary_name = "google-maps-scraper.exe" if platform == "windows" else "google-maps-scraper"
        binary_path = extract_dir / binary_name

        if binary_path.exists():
            # Make executable on Unix
            if platform != "windows":
                binary_path.chmod(0o755)
            logger.info(f"Binary extracted to: {binary_path}")
            return str(binary_path)
        else:
            logger.error(f"Binary not found in extracted files: {binary_path}")
            return None

    except Exception as e:
        logger.error(f"Error downloading binary: {e}")
        return None


def build_scraper_from_source() -> Optional[str]:
    """Build scraper from source (requires Go)."""
    import subprocess

    try:
        repo_dir = Path.cwd() / "google-maps-scraper-source"

        # Clone if not exists
        if not repo_dir.exists():
            logger.info("Cloning google-maps-scraper repository...")
            subprocess.run(
                ["git", "clone", "https://github.com/gosom/google-maps-scraper.git", str(repo_dir)],
                check=True
            )

        # Build
        logger.info("Building google-maps-scraper...")
        result = subprocess.run(
            ["go", "build", "-o", "google-maps-scraper"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Build failed: {result.stderr}")
            return None

        # Copy binary to working directory
        binary_src = repo_dir / ("google-maps-scraper.exe" if os.name == 'nt' else "google-maps-scraper")
        binary_dst = Path.cwd() / binary_src.name

        shutil.copy2(binary_src, binary_dst)

        if os.name != 'nt':
            binary_dst.chmod(0o755)

        logger.info(f"Binary built and copied to: {binary_dst}")
        return str(binary_dst)

    except Exception as e:
        logger.error(f"Error building from source: {e}")
        return None