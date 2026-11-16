"""Scraper runner - orchestrates the scraping process."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from utils.config_loader import get_settings
from utils.logging import get_logger
from utils.helpers import generate_id, chunk_list
from storage.master_db import get_master_db, ScrapingJobModel
from storage.models import ScrapingJob, ScrapedLead
from .wrapper import GoogleMapsScraperWrapper, ScraperResult
from .queries import QueryGenerator

logger = get_logger(__name__)


@dataclass
class ScrapingRunResult:
    """Result of a complete scraping run."""
    success: bool
    total_queries: int
    successful_queries: int
    failed_queries: int
    total_results: int
    unique_leads: int
    duration_seconds: float
    errors: List[str]
    job_ids: List[str]


class ScraperRunner:
    """Orchestrates scraping runs."""

    def __init__(self, config: Optional[Dict] = None):
        self.settings = get_settings()
        self.config = config or {}
        self.db = get_master_db()
        self.wrapper = GoogleMapsScraperWrapper(config)
        self.query_generator = QueryGenerator()

        # Output directory
        self.output_dir = Path(self.settings.output_dir) / "scraper_results"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_full_scrape(
        self,
        queries: List[str] = None,
        priorities: List[int] = None,
        max_queries: int = None,
        batch_size: int = None
    ) -> ScrapingRunResult:
        """Run complete scraping process."""
        start_time = time.time()

        # Generate queries if not provided
        if queries is None:
            logger.info("Generating queries...")
            queries = self.query_generator.generate_all_queries(
                priorities=priorities or [1, 2],
                max_per_state=max_queries
            )

        # Apply limit
        if max_queries and len(queries) > max_queries:
            queries = queries[:max_queries]

        logger.info(f"Starting scraping run with {len(queries)} queries")

        # Save queries
        query_file = self.query_generator.save_queries(
            queries,
            f"queries_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        # Create scraping job record
        job = ScrapingJob(
            id=generate_id("job"),
            query=f"batch_run_{len(queries)}_queries",
            status="running",
            started_at=datetime.utcnow(),
            params={
                "query_count": len(queries),
                "priorities": priorities,
                "max_queries": max_queries,
                "query_file": query_file,
            }
        )
        job_model = self.db.create_scraping_job(job)
        job_id = job_model.id

        # Process in batches
        batch_size = batch_size or self.settings.perf_batch_size_scrape
        query_batches = chunk_list(queries, batch_size)

        all_results = []
        all_leads = []
        errors = []
        successful = 0
        failed = 0

        for i, batch in enumerate(query_batches):
            logger.info(f"Processing batch {i+1}/{len(query_batches)} ({len(batch)} queries)")

            # Create batch query file
            batch_file = self.output_dir / f"batch_{i}_{generate_id()}.txt"
            with open(batch_file, 'w', encoding='utf-8') as f:
                for q in batch:
                    f.write(f"{q}\n")

            # Output file for this batch
            output_file = self.output_dir / f"results_batch_{i}_{generate_id()}.json"

            # Run scraper
            result = self.wrapper._run_scraper_batch(batch_file, output_file)

            if result.success:
                successful += 1
                all_results.append(result)

                # Convert to leads
                leads = self.wrapper.convert_to_scraped_leads(result.results, f"batch_{i}")
                all_leads.extend(leads)

                # Save leads to database
                self._save_leads(leads)
            else:
                failed += 1
                errors.append(f"Batch {i}: {result.error}")
                logger.error(f"Batch {i} failed: {result.error}")

            # Cleanup batch file
            try:
                batch_file.unlink()
            except:
                pass

            # Rate limiting between batches
            if i < len(query_batches) - 1:
                time.sleep(2)

        # Update job record
        duration = time.time() - start_time
        self.db.update_scraping_job(
            job_id,
            status="completed" if failed == 0 else "partial",
            completed_at=datetime.utcnow(),
            results_count=len(all_leads),
            output_file=str(self.output_dir),
        )

        # Deduplicate leads
        unique_leads = self._deduplicate_leads(all_leads)

        logger.info(f"Scraping run completed in {duration:.1f}s")
        logger.info(f"Successful: {successful}, Failed: {failed}, Total leads: {len(all_leads)}, Unique: {len(unique_leads)}")

        return ScrapingRunResult(
            success=failed == 0,
            total_queries=len(queries),
            successful_queries=successful,
            failed_queries=failed,
            total_results=len(all_leads),
            unique_leads=len(unique_leads),
            duration_seconds=duration,
            errors=errors,
            job_ids=[job_id]
        )

    def run_incremental_scrape(
        self,
        new_queries: List[str],
        batch_size: int = None
    ) -> ScrapingRunResult:
        """Run scraping for new queries only."""
        return self.run_full_scrape(
            queries=new_queries,
            batch_size=batch_size
        )

    def _save_leads(self, leads: List[ScrapedLead]) -> int:
        """Save leads to database."""
        saved = 0
        for lead in leads:
            try:
                self.db.upsert_scraped_lead(lead)
                saved += 1
            except Exception as e:
                logger.warning(f"Error saving lead: {e}")
        return saved

    def _deduplicate_leads(self, leads: List[ScrapedLead]) -> List[ScrapedLead]:
        """Deduplicate leads by place_id or name+city+state."""
        seen = set()
        unique = []

        for lead in leads:
            # Create dedup key
            if lead.place_id:
                key = f"place:{lead.place_id}"
            elif lead.name and lead.city and lead.state:
                key = f"name:{lead.name.lower()}:{lead.city.lower()}:{lead.state.upper()}"
            else:
                key = f"raw:{generate_id(lead.name, lead.address, lead.phone)}"

            if key not in seen:
                seen.add(key)
                unique.append(lead)

        return unique

    def run_continuous(
        self,
        interval_hours: int = 24,
        max_runs: int = None,
        priorities: List[int] = None
    ) -> None:
        """Run continuous scraping loop."""
        run_count = 0

        while max_runs is None or run_count < max_runs:
            logger.info(f"Starting continuous run #{run_count + 1}")

            try:
                result = self.run_full_scrape(priorities=priorities)
                logger.info(f"Run #{run_count + 1} completed: {result.unique_leads} unique leads")
            except Exception as e:
                logger.error(f"Run #{run_count + 1} failed: {e}")

            run_count += 1

            if max_runs is None or run_count < max_runs:
                logger.info(f"Sleeping for {interval_hours} hours...")
                time.sleep(interval_hours * 3600)

        logger.info("Continuous scraping completed")

    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get scraping statistics."""
        with self.db.get_session() as session:
            from sqlalchemy import func

            # Job stats
            total_jobs = session.query(func.count(ScrapingJobModel.id)).scalar()
            completed_jobs = session.query(func.count(ScrapingJobModel.id)).filter(
                ScrapingJobModel.status == 'completed'
            ).scalar()
            failed_jobs = session.query(func.count(ScrapingJobModel.id)).filter(
                ScrapingJobModel.status == 'failed'
            ).scalar()

            # Lead stats
            total_leads = session.query(func.count(ScrapedLeadModel.id)).scalar()

            return {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'total_scraped_leads': total_leads,
            }


from storage.master_db import ScrapedLeadModel