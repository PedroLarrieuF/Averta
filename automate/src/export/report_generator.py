"""Report generation for daily execution."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from utils.config_loader import get_settings
from utils.logging import get_logger
from storage.master_db import get_master_db
from storage.models import DailyReport, QualifiedLead, LeadClassification
from .excel_exporter import ExcelExporter

logger = get_logger(__name__)


@dataclass
class ReportData:
    """Collected data for report generation."""
    date: date
    scraping_stats: Dict[str, Any]
    qualification_stats: Dict[str, Any]
    coverage_stats: Dict[str, Any]
    leads_sample: List[QualifiedLead]
    errors: List[str]
    warnings: List[str]
    started_at: datetime
    completed_at: datetime


class ReportGenerator:
    """Generates daily execution reports."""

    def __init__(self):
        self.settings = get_settings()
        self.db = get_master_db()
        self.exporter = ExcelExporter()

    def generate_daily_report(
        self,
        report_date: date = None,
        scraping_result: Any = None,
        qualification_result: Any = None,
        started_at: datetime = None,
        completed_at: datetime = None
    ) -> DailyReport:
        """Generate complete daily report."""
        if report_date is None:
            report_date = date.today()

        if started_at is None:
            started_at = datetime.utcnow()

        if completed_at is None:
            completed_at = datetime.utcnow()

        duration = (completed_at - started_at).total_seconds()

        # Collect stats
        scraping_stats = scraping_result or {}
        qualification_stats = qualification_result or {}
        coverage_stats = self.db.get_coverage_stats()

        # Get sample leads for report
        leads_a = self.db.get_leads_by_classification(LeadClassification.A, limit=10)
        leads_b = self.db.get_leads_by_classification(LeadClassification.B, limit=10)
        leads_sample = leads_a + leads_b

        # Calculate KPIs
        total_qualified = coverage_stats.get('total_qualified', 0)
        leads_a_count = coverage_stats.get('by_classification', {}).get('A', 0)
        leads_b_count = coverage_stats.get('by_classification', {}).get('B', 0)
        qualified_with_contact = (
            coverage_stats.get('with_email', 0) +
            coverage_stats.get('with_phone', 0) +
            coverage_stats.get('with_whatsapp', 0)
        )

        cost_per_qualified = 0.0
        if leads_a_count + leads_b_count > 0:
            # Simplified cost calculation
            cost_per_qualified = 10.0  # Placeholder

        qualification_rate = 0.0
        total_processed = scraping_stats.get('total_results', 1)
        if total_processed > 0:
            qualification_rate = ((leads_a_count + leads_b_count) / total_processed) * 100

        # Build report
        report = DailyReport(
            date=report_date,
            queries_executed=scraping_stats.get('total_queries', 0),
            companies_found=scraping_stats.get('total_results', 0),
            unique_companies=scraping_stats.get('unique_leads', 0),
            leads_classified_a=leads_a_count,
            leads_classified_b=leads_b_count,
            leads_classified_c=coverage_stats.get('by_classification', {}).get('C', 0),
            leads_classified_d=coverage_stats.get('by_classification', {}).get('D', 0),
            leads_discarded=scraping_stats.get('failed_queries', 0),
            decision_makers_identified=qualification_stats.get('decision_makers_found', 0),
            institutional_contacts_valid=qualification_stats.get('institutional_contacts', 0),
            business_phones_valid=coverage_stats.get('with_phone', 0),
            corporate_emails_found=coverage_stats.get('with_email', 0),
            linkedin_verified=coverage_stats.get('with_linkedin', 0),
            states_covered=len(coverage_stats.get('by_state', {})),
            segments_covered=len(coverage_stats.get('by_segment', {})),
            cost_per_qualified_lead=cost_per_qualified,
            qualification_rate=round(qualification_rate, 2),
            started_at=started_at,
            completed_at=completed_at,
            duration_seconds=duration,
            errors=scraping_stats.get('errors', []),
            warnings=[],
        )

        # Save to database
        self.db.upsert_daily_report(report)

        # Export to Excel
        self.exporter.export_daily_report(report)

        # Export coverage report
        self.exporter.export_coverage_report(coverage_stats)

        logger.info(f"Daily report generated for {report_date}")
        return report

    def generate_weekly_report(
        self,
        end_date: date = None,
        weeks_back: int = 1
    ) -> Dict[str, Any]:
        """Generate weekly aggregated report."""
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(weeks=weeks_back)

        # Get daily reports for period
        daily_reports = self.db.get_recent_reports(days=weeks_back * 7)
        period_reports = [r for r in daily_reports if start_date <= r.report_date <= end_date]

        if not period_reports:
            logger.warning(f"No reports found for period {start_date} to {end_date}")
            return {}

        # Aggregate
        agg = {
            'period': f"{start_date} a {end_date}",
            'total_days': len(period_reports),
            'total_queries': sum(r.queries_executed for r in period_reports),
            'total_companies_found': sum(r.companies_found for r in period_reports),
            'total_unique_companies': sum(r.unique_companies for r in period_reports),
            'total_leads_a': sum(r.leads_classified_a for r in period_reports),
            'total_leads_b': sum(r.leads_classified_b for r in period_reports),
            'total_leads_c': sum(r.leads_classified_c for r in period_reports),
            'total_leads_d': sum(r.leads_classified_d for r in period_reports),
            'total_decision_makers': sum(r.decision_makers_identified for r in period_reports),
            'avg_qualification_rate': sum(r.qualification_rate for r in period_reports) / len(period_reports),
            'avg_cost_per_lead': sum(r.cost_per_qualified_lead for r in period_reports) / len(period_reports),
            'states_covered': set(),
            'segments_covered': set(),
        }

        # Collect unique states/segments from coverage stats
        for report in period_reports:
            # Would need to query historical coverage
            pass

        return agg

    def generate_lead_quality_report(self) -> Dict[str, Any]:
        """Generate lead quality analysis report."""
        coverage = self.db.get_coverage_stats()

        # Get leads by classification
        leads_a = self.db.get_leads_by_classification(LeadClassification.A, limit=1000)
        leads_b = self.db.get_leads_by_classification(LeadClassification.B, limit=1000)
        leads_c = self.db.get_leads_by_classification(LeadClassification.C, limit=1000)

        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'summary': {
                'total_qualified': coverage.get('total_qualified', 0),
                'leads_a': len(leads_a),
                'leads_b': len(leads_b),
                'leads_c': len(leads_c),
                'whatsapp_ready': coverage.get('whatsapp_ready', 0),
            },
            'contact_completeness': self._analyze_contact_completeness(leads_a + leads_b + leads_c),
            'segment_distribution': self._analyze_segment_distribution(leads_a + leads_b),
            'geographic_distribution': self._analyze_geographic_distribution(leads_a + leads_b),
            'score_distribution': self._analyze_score_distribution(leads_a + leads_b + leads_c),
            'top_companies': self._get_top_companies(leads_a + leads_b, 20),
        }

        return report

    def _analyze_contact_completeness(self, leads: List[QualifiedLead]) -> Dict[str, Any]:
        """Analyze contact data completeness."""
        if not leads:
            return {}

        total = len(leads)

        return {
            'with_phone': sum(1 for l in leads if l.phone) / total * 100,
            'with_verified_phone': sum(1 for l in leads if l.phone_verified) / total * 100,
            'with_whatsapp': sum(1 for l in leads if l.whatsapp) / total * 100,
            'with_verified_whatsapp': sum(1 for l in leads if l.whatsapp_verified) / total * 100,
            'with_email': sum(1 for l in leads if l.email) / total * 100,
            'with_verified_email': sum(1 for l in leads if l.email_verified) / total * 100,
            'with_website': sum(1 for l in leads if l.website) / total * 100,
            'with_linkedin': sum(1 for l in leads if l.linkedin) / total * 100,
            'with_decision_makers': sum(1 for l in leads if l.decision_makers) / total * 100,
            'whatsapp_ready': sum(1 for l in leads if l.whatsapp_ready) / total * 100,
        }

    def _analyze_segment_distribution(self, leads: List[QualifiedLead]) -> Dict[str, int]:
        """Analyze segment distribution."""
        dist = {}
        for lead in leads:
            seg = lead.segment or 'não identificado'
            dist[seg] = dist.get(seg, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: -x[1]))

    def _analyze_geographic_distribution(self, leads: List[QualifiedLead]) -> Dict[str, int]:
        """Analyze geographic distribution."""
        dist = {}
        for lead in leads:
            state = lead.state or 'não identificado'
            dist[state] = dist.get(state, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: -x[1]))

    def _analyze_score_distribution(self, leads: List[QualifiedLead]) -> Dict[str, Any]:
        """Analyze score distribution."""
        if not leads:
            return {}

        scores = [l.score for l in leads]

        return {
            'min': min(scores),
            'max': max(scores),
            'avg': sum(scores) / len(scores),
            'median': sorted(scores)[len(scores) // 2],
            'ranges': {
                '90-100': sum(1 for s in scores if s >= 90),
                '80-89': sum(1 for s in scores if 80 <= s < 90),
                '70-79': sum(1 for s in scores if 70 <= s < 80),
                '60-69': sum(1 for s in scores if 60 <= s < 70),
                '50-59': sum(1 for s in scores if 50 <= s < 60),
                '<50': sum(1 for s in scores if s < 50),
            }
        }

    def _get_top_companies(self, leads: List[QualifiedLead], limit: int) -> List[Dict]:
        """Get top companies by score."""
        sorted_leads = sorted(leads, key=lambda l: -l.score)
        top = sorted_leads[:limit]

        return [
            {
                'name': l.name,
                'trade_name': l.trade_name,
                'segment': l.segment,
                'city': l.city,
                'state': l.state,
                'score': l.score,
                'classification': l.classification.value,
                'has_phone': bool(l.phone),
                'has_email': bool(l.email),
                'has_decision_makers': bool(l.decision_makers),
            }
            for l in top
        ]

    def export_all_reports(self, report_date: date = None) -> Dict[str, str]:
        """Export all report types for a date."""
        if report_date is None:
            report_date = date.today()

        files = {}

        # Generate daily report
        report = self.generate_daily_report(report_date)
        files['daily'] = report.report_file or ""

        # Export leads A/B
        leads_ab = self.db.get_leads_for_export()
        files['leads_ab'] = self.exporter.export_leads_ab(leads_ab)

        # Export leads C
        leads_c = self.db.get_leads_by_classification(LeadClassification.C, limit=5000)
        files['leads_c'] = self.exporter.export_leads_c(leads_c)

        # Export WhatsApp ready
        leads_wa = self.db.get_leads_for_whatsapp()
        files['whatsapp'] = self.exporter.export_whatsapp_ready(leads_wa)

        # Export decision makers
        files['decision_makers'] = self.exporter.export_decision_makers_report(leads_ab)

        # Generate coverage report
        coverage = self.db.get_coverage_stats()
        files['coverage'] = self.exporter.export_coverage_report(coverage)

        return files