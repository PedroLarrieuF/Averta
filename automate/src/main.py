"""
Main entry point for Averta Lead Generation Automation.

This module orchestrates the complete lead generation pipeline:
1. Query generation based on ICP and national coverage
2. Scraping using google-maps-scraper
3. Lead qualification and scoring
4. Data enrichment
5. Export to Excel and reports
6. WhatsApp Business preparation and messaging
7. Email outreach preparation and sending
"""

import argparse
import asyncio
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List

from .utils.config_loader import get_settings, reload_settings
from .utils.logging import get_logger, setup_logging
from .scraper.queries import QueryGenerator
from .scraper.runner import ScraperRunner
from .qualification.scorer import LeadQualificationPipeline
from .qualification.enricher import LeadEnricher
from .export.excel_exporter import ExcelExporter
from .export.report_generator import ReportGenerator
from .whatsapp.prepare import WhatsAppPreparator
from .whatsapp.client import (
    IntelligentMessagingEngine,
    CampaignBuilder,
    Campaign,
    WhatsAppProvider,
    LeadClassification,
)
from .email_outreach.prepare import EmailPreparator
from .email_outreach.client import (
    IntelligentEmailEngine,
    EmailCampaignBuilder,
    EmailCampaign,
    EmailProvider,
    EmailStatus,
    CampaignStage,
    LeadClassification as EmailLeadClassification,
)
from .storage.master_db import init_master_db, get_master_db
from .storage.models import QualifiedLead, DecisionMaker

logger = get_logger(__name__)


class LeadGenerationAutomation:
    """Main automation orchestrator."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            reload_settings(config_path)

        self.settings = get_settings()
        self.db = init_master_db()

        # Initialize components
        self.query_generator = QueryGenerator()
        self.scraper_runner = ScraperRunner()
        self.qualification_pipeline = LeadQualificationPipeline()
        self.enricher = LeadEnricher()
        self.excel_exporter = ExcelExporter()
        self.report_generator = ReportGenerator()
        self.whatsapp_preparator = WhatsAppPreparator()
        self.email_preparator = EmailPreparator()
        self.messaging_engine: Optional[IntelligentMessagingEngine] = None
        self.email_engine: Optional[IntelligentEmailEngine] = None

        logger.info("Lead Generation Automation initialized")

    async def _get_messaging_engine(self) -> IntelligentMessagingEngine:
        """Get or create WhatsApp messaging engine."""
        if self.messaging_engine is None:
            provider_type = WhatsAppProvider(self.settings.__dict__.get('whatsapp_provider', 'cloud_api'))
            self.messaging_engine = await create_messaging_engine(provider_type)
        return self.messaging_engine

    async def _get_email_engine(self) -> IntelligentEmailEngine:
        """Get or create email engine."""
        if self.email_engine is None:
            provider_type = EmailProvider(self.settings.__dict__.get('email_provider', 'smtp'))
            self.email_engine = await create_email_engine(provider_type)
        return self.email_engine

    def run_whatsapp_campaign(
        self,
        campaign_name: str = None,
        classifications: List[str] = None,
        min_score: float = 70,
        max_messages_per_lead: int = 3,
        segments: List[str] = None,
        states: List[str] = None,
        dry_run: bool = True,
    ) -> dict:
        """Run a WhatsApp campaign against qualified leads."""

        if not self.settings.__dict__.get('whatsapp_enabled', False):
            return {
                'success': False,
                'error': 'WhatsApp not enabled in settings. Set whatsapp.enabled: true in config/settings.yaml'
            }

        # Build campaign
        builder = CampaignBuilder(campaign_name or f"Campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        if classifications:
            class_enums = [LeadClassification(c) for c in classifications]
            builder.targeting_classifications(*class_enums)

        builder.targeting_min_score(min_score)
        builder.max_messages_per_lead(max_messages_per_lead)

        if segments:
            builder.targeting_segments(*segments)
        if states:
            builder.targeting_states(*states)

        # Get campaign config from settings
        wa_campaign = self.settings.__dict__.get('whatsapp_campaigns', {}).get('default', {})

        if wa_campaign:
            builder.with_templates(
                initial=wa_campaign.get('initial_template', 'initial_contact'),
                follow_ups=wa_campaign.get('follow_up_templates', ['follow_up_1', 'follow_up_2', 'value_proposition']),
                intervals_hours=wa_campaign.get('follow_up_intervals_hours', [24, 72, 168])
            )
            builder.with_schedule(
                business_hours_only=wa_campaign.get('business_hours_only', True),
                start_hour=wa_campaign.get('business_hours_start', 8),
                end_hour=wa_campaign.get('business_hours_end', 18),
                timezone=wa_campaign.get('timezone', 'America/Sao_Paulo'),
                rate_per_minute=wa_campaign.get('rate_limit_per_minute', 20),
                rate_per_hour=wa_campaign.get('rate_limit_per_hour', 500),
                rate_per_day=wa_campaign.get('rate_limit_per_day', 2000)
            )

        campaign = builder.build()

        # Get leads from database
        leads = self._get_leads_for_campaign(campaign)

        if not leads:
            return {
                'success': True,
                'message': 'No leads match campaign criteria',
                'leads_found': 0,
            }

        logger.info(f"Found {len(leads)} leads for campaign '{campaign.name}'")

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'campaign': campaign.name,
                'leads_found': len(leads),
                'leads_preview': [
                    {
                        'id': l.id,
                        'name': l.name,
                        'segment': l.segment,
                        'city': l.city,
                        'state': l.state,
                        'score': l.score,
                        'classification': l.classification.value,
                        'whatsapp': l.whatsapp,
                        'has_decision_maker': len(l.decision_makers) > 0,
                    }
                    for l in leads[:10]
                ],
            }

        # Get decision makers
        decision_makers_map = {}
        for lead in leads:
            if lead.decision_makers:
                decision_makers_map[lead.id] = lead.decision_makers[0]

        # Run campaign asynchronously
        return asyncio.run(self._run_campaign_async(campaign, leads, decision_makers_map))

    async def _run_campaign_async(
        self,
        campaign: Campaign,
        leads: List[QualifiedLead],
        decision_makers_map: dict
    ) -> dict:
        """Run campaign asynchronously."""
        engine = await self._get_messaging_engine()
        engine.register_campaign(campaign)

        results = await engine.run_campaign(campaign, leads, decision_makers_map)

        return {
            'success': True,
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'results': results,
        }

    def _get_leads_for_campaign(self, campaign: Campaign) -> List[QualifiedLead]:
        """Get leads matching campaign criteria."""
        all_leads = []

        for cls in campaign.lead_classifications:
            leads = self.db.get_leads_by_classification(cls, limit=10000)
            all_leads.extend(leads)

        # Filter by score
        all_leads = [l for l in all_leads if l.score >= campaign.min_score]

        # Filter by segments
        if campaign.segments:
            all_leads = [l for l in all_leads if l.segment in campaign.segments]

        # Filter by states
        if campaign.states:
            all_leads = [l for l in all_leads if l.state in campaign.states]

        # Filter: must have WhatsApp or phone
        all_leads = [l for l in all_leads if l.whatsapp or l.phone]

        # Filter: not opted out
        if campaign.respect_opt_out:
            # Would check opt-out status from conversation tracking
            pass

        return all_leads

    def send_whatsapp_test(
        self,
        lead_id: str,
        template_name: str = "initial_contact",
        custom_text: str = None,
    ) -> dict:
        """Send a test WhatsApp message to a specific lead."""

        if not self.settings.__dict__.get('whatsapp_enabled', False):
            return {
                'success': False,
                'error': 'WhatsApp not enabled in settings'
            }

        # Get lead
        lead = self.db.get_qualified_lead(lead_id)
        if not lead:
            return {'success': False, 'error': f'Lead {lead_id} not found'}

        # Get decision maker
        dm = lead.decision_makers[0] if lead.decision_makers else None

        # Create message
        async def send_test():
            engine = await self._get_messaging_engine()

            if custom_text:
                message = engine.create_custom_message(
                    lead=lead,
                    text=custom_text,
                    decision_maker=dm,
                )
            else:
                message = engine.create_personalized_message(
                    lead=lead,
                    template_name=template_name,
                    decision_maker=dm,
                )

            result = await engine.send_message(message)
            return result

        return asyncio.run(send_test())

    def get_whatsapp_campaign_stats(self, campaign_id: str = None) -> dict:
        """Get WhatsApp campaign statistics."""
        if self.messaging_engine is None:
            return {'error': 'Messaging engine not initialized'}

        if campaign_id:
            campaign = self.messaging_engine.get_campaign(campaign_id)
            if campaign:
                return {
                    'campaign_id': campaign.id,
                    'name': campaign.name,
                    'stats': campaign.stats,
                    'active': campaign.active,
                }
            return {'error': 'Campaign not found'}

        # Return all campaigns
        return {
            campaign_id: {
                'name': c.name,
                'stats': c.stats,
                'active': c.active,
            }
            for campaign_id, c in self.messaging_engine.campaigns.items()
        }

    # ============================================================
    # EMAIL CAMPAIGN METHODS
    # ============================================================

    def run_email_campaign(
        self,
        campaign_name: str = None,
        classifications: List[str] = None,
        min_score: float = 70,
        max_emails_per_lead: int = 4,
        segments: List[str] = None,
        states: List[str] = None,
        dry_run: bool = True,
    ) -> dict:
        """Run an email campaign against qualified leads."""

        if not self.settings.__dict__.get('email_enabled', False):
            return {
                'success': False,
                'error': 'Email not enabled in settings. Set email.enabled: true in config/settings.yaml'
            }

        # Build campaign
        builder = EmailCampaignBuilder(campaign_name or f"Email_Campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        if classifications:
            class_enums = [EmailLeadClassification(c) for c in classifications]
            builder.targeting_classifications(*class_enums)

        builder.targeting_min_score(min_score)
        builder.max_emails_per_lead(max_emails_per_lead)

        if segments:
            builder.targeting_segments(*segments)
        if states:
            builder.targeting_states(*states)

        # Get campaign config from settings
        email_campaign = self.settings.__dict__.get('email_campaigns', {}).get('default', {})

        if email_campaign:
            # Convert sequence format
            sequence = []
            for step in email_campaign.get('sequence', []):
                stage_map = {
                    'initial': CampaignStage.INITIAL,
                    'follow_up_1': CampaignStage.FOLLOW_UP_1,
                    'follow_up_2': CampaignStage.FOLLOW_UP_2,
                    'follow_up_3': CampaignStage.FOLLOW_UP_3,
                }
                sequence.append({
                    "template": step.get('template', 'initial_outreach'),
                    "delay_days": step.get('delay_days', 0),
                    "stage": stage_map.get(step.get('stage', 'initial'), CampaignStage.INITIAL)
                })
            builder.with_sequence(sequence)

            builder.with_schedule(
                business_hours_only=email_campaign.get('business_hours_only', True),
                start_hour=email_campaign.get('business_hours_start', 8),
                end_hour=email_campaign.get('business_hours_end', 18),
                timezone=email_campaign.get('timezone', 'America/Sao_Paulo'),
                days_of_week=email_campaign.get('days_of_week', [0, 1, 2, 3, 4]),
                rate_per_minute=email_campaign.get('rate_limit_per_minute', 10),
                rate_per_hour=email_campaign.get('rate_limit_per_hour', 200),
                rate_per_day=email_campaign.get('rate_limit_per_day', 1000)
            )

        campaign = builder.build()

        # Get leads from database
        leads = self._get_leads_for_email_campaign(campaign)

        if not leads:
            return {
                'success': True,
                'message': 'No leads match campaign criteria',
                'leads_found': 0,
            }

        logger.info(f"Found {len(leads)} leads for email campaign '{campaign.name}'")

        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'campaign': campaign.name,
                'leads_found': len(leads),
                'leads_preview': [
                    {
                        'id': l.id,
                        'name': l.name,
                        'segment': l.segment,
                        'city': l.city,
                        'state': l.state,
                        'score': l.score,
                        'classification': l.classification.value,
                        'email': l.email,
                        'has_decision_maker': len(l.decision_makers) > 0,
                    }
                    for l in leads[:10]
                ],
            }

        # Get decision makers
        decision_makers_map = {}
        for lead in leads:
            if lead.decision_makers:
                decision_makers_map[lead.id] = lead.decision_makers[0]

        # Run campaign asynchronously
        return asyncio.run(self._run_email_campaign_async(campaign, leads, decision_makers_map))

    async def _run_email_campaign_async(
        self,
        campaign: EmailCampaign,
        leads: List[QualifiedLead],
        decision_makers_map: dict
    ) -> dict:
        """Run email campaign asynchronously."""
        engine = await self._get_email_engine()
        engine.register_campaign(campaign)

        results = await engine.run_full_campaign(campaign, leads, decision_makers_map)

        return {
            'success': True,
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'results': results,
        }

    def _get_leads_for_email_campaign(self, campaign: EmailCampaign) -> List[QualifiedLead]:
        """Get leads matching email campaign criteria."""
        all_leads = []

        for cls in campaign.lead_classifications:
            leads = self.db.get_leads_by_classification(cls, limit=10000)
            all_leads.extend(leads)

        # Filter by score
        all_leads = [l for l in all_leads if l.score >= campaign.min_score]

        # Filter by segments
        if campaign.segments:
            all_leads = [l for l in all_leads if l.segment in campaign.segments]

        # Filter by states
        if campaign.states:
            all_leads = [l for l in all_leads if l.state in campaign.states]

        # Filter: must have email
        if campaign.has_email_only:
            all_leads = [l for l in all_leads if l.email and normalize_email(l.email)]

        # Filter: not opted out
        if campaign.respect_opt_out:
            # Would check opt-out status from conversation tracking
            pass

        return all_leads

    def send_email_test(
        self,
        lead_id: str,
        template_name: str = "initial_outreach",
        custom_subject: str = None,
        custom_html: str = None,
        custom_text: str = None,
    ) -> dict:
        """Send a test email to a specific lead."""

        if not self.settings.__dict__.get('email_enabled', False):
            return {
                'success': False,
                'error': 'Email not enabled in settings'
            }

        # Get lead
        lead = self.db.get_qualified_lead(lead_id)
        if not lead:
            return {'success': False, 'error': f'Lead {lead_id} not found'}

        if not lead.email:
            return {'success': False, 'error': f'Lead {lead_id} has no email'}

        # Get decision maker
        dm = lead.decision_makers[0] if lead.decision_makers else None

        # Create message
        async def send_test():
            engine = await self._get_email_engine()

            if custom_subject or custom_html or custom_text:
                message = engine.create_custom_email(
                    lead=lead,
                    subject=custom_subject or "Teste Averta",
                    html_body=custom_html or "<p>Teste</p>",
                    text_body=custom_text or "Teste",
                    decision_maker=dm,
                )
            else:
                message = engine.create_personalized_email(
                    lead=lead,
                    template_name=template_name,
                    decision_maker=dm,
                )

            result = await engine.send_email(message)
            return result

        return asyncio.run(send_test())

    def get_email_campaign_stats(self, campaign_id: str = None) -> dict:
        """Get email campaign statistics."""
        if self.email_engine is None:
            return {'error': 'Email engine not initialized'}

        if campaign_id:
            campaign = self.email_engine.get_campaign(campaign_id)
            if campaign:
                return {
                    'campaign_id': campaign.id,
                    'name': campaign.name,
                    'stats': campaign.stats,
                    'active': campaign.active,
                }
            return {'error': 'Campaign not found'}

        # Return all campaigns
        return {
            campaign_id: {
                'name': c.name,
                'stats': c.stats,
                'active': c.active,
            }
            for campaign_id, c in self.email_engine.campaigns.items()
        }

    def prepare_email_contacts(
        self,
        classifications: List[str] = None,
        min_score: float = 50,
        segments: List[str] = None,
        states: List[str] = None,
        export_csv: bool = True,
        export_sendgrid: bool = False,
    ) -> dict:
        """Prepare and export email contacts for campaigns."""

        # Get leads
        class_enums = [EmailLeadClassification(c) for c in classifications] if classifications else [EmailLeadClassification.A, EmailLeadClassification.B]

        leads = []
        for cls in class_enums:
            leads.extend(self.db.get_leads_by_classification(cls, limit=10000))

        # Filter
        leads = [l for l in leads if l.score >= min_score]
        if segments:
            leads = [l for l in leads if l.segment in segments]
        if states:
            leads = [l for l in leads if l.state in states]

        # Prepare contacts
        contacts = self.email_preparator.prepare_leads(
            leads,
            classifications=class_enums,
            min_score=min_score,
            segment_filter=segments,
            state_filter=states
        )

        if not contacts:
            return {'success': True, 'message': 'No contacts prepared', 'contacts': 0}

        # Schedule sends
        contacts = self.email_preparator.get_sending_schedule(contacts)

        # Export
        files = {}
        if export_csv:
            files['csv'] = self.email_preparator.export_for_email_api(contacts)
        if export_sendgrid:
            files['sendgrid'] = self.email_preparator.export_for_sendgrid(contacts)

        # Stats
        stats = self.email_preparator.get_stats(contacts)

        return {
            'success': True,
            'contacts_prepared': len(contacts),
            'export_files': files,
            'stats': stats,
            'preview': self.email_preparator.preview_contacts(contacts, 10)
        }

    def run_full_pipeline(
        self,
        priorities: List[int] = None,
        max_queries: int = None,
        max_leads: int = None,
        skip_scraping: bool = False,
        skip_qualification: bool = False,
        skip_enrichment: bool = False,
        skip_export: bool = False,
    ) -> dict:
        """Run the complete lead generation pipeline."""
        start_time = time.time()
        started_at = datetime.utcnow()

        logger.info("=" * 60)
        logger.info("STARTING FULL LEAD GENERATION PIPELINE")
        logger.info("=" * 60)

        results = {
            'success': True,
            'started_at': started_at.isoformat(),
            'steps': {},
            'errors': [],
            'warnings': [],
        }

        try:
            # Step 1: Generate Queries
            logger.info("STEP 1: Generating queries...")
            step_start = time.time()

            queries = self.query_generator.generate_all_queries(
                priorities=priorities or [1, 2],
                max_per_state=max_queries
            )

            if max_queries and len(queries) > max_queries:
                queries = queries[:max_queries]

            query_file = self.query_generator.save_queries(
                queries,
                f"queries_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )

            results['steps']['query_generation'] = {
                'queries_generated': len(queries),
                'query_file': query_file,
                'duration_seconds': time.time() - step_start,
            }
            logger.info(f"Generated {len(queries)} queries")

            # Step 2: Scraping
            scraped_leads = []
            if not skip_scraping:
                logger.info("STEP 2: Running scraper...")
                step_start = time.time()

                scrape_result = self.scraper_runner.run_full_scrape(
                    queries=queries,
                    batch_size=self.settings.perf_batch_size_scrape
                )

                # Get scraped leads from database
                scraped_leads = self.db.get_unqualified_leads(limit=max_leads or 50000)

                results['steps']['scraping'] = {
                    'total_queries': scrape_result.total_queries,
                    'successful_queries': scrape_result.successful_queries,
                    'failed_queries': scrape_result.failed_queries,
                    'total_results': scrape_result.total_results,
                    'unique_leads': scrape_result.unique_leads,
                    'duration_seconds': scrape_result.duration_seconds,
                    'errors': scrape_result.errors,
                }
                logger.info(f"Scraping completed: {scrape_result.unique_leads} unique leads")
            else:
                logger.info("STEP 2: Skipping scraping (using existing leads)")
                scraped_leads = self.db.get_unqualified_leads(limit=max_leads or 50000)
                results['steps']['scraping'] = {'skipped': True, 'leads_used': len(scraped_leads)}

            # Step 3: Qualification
            qualified_leads = []
            if not skip_qualification:
                logger.info("STEP 3: Qualifying leads...")
                step_start = time.time()

                # Convert scraped leads to dict format
                leads_data = [lead.to_dict() for lead in scraped_leads]

                # Qualify in batches
                batch_size = self.settings.perf_batch_size_qualify
                all_qualified = []

                for i in range(0, len(leads_data), batch_size):
                    batch = leads_data[i:i + batch_size]
                    qualified_batch = self.qualification_pipeline.qualify_batch(batch)
                    all_qualified.extend(qualified_batch)

                    # Save to database
                    for lead in qualified_batch:
                        self.db.upsert_qualified_lead(lead)

                qualified_leads = all_qualified

                qual_stats = self.qualification_pipeline.get_stats()

                results['steps']['qualification'] = {
                    'total_processed': qual_stats['total'],
                    'classified_a': qual_stats['classified_a'],
                    'classified_b': qual_stats['classified_b'],
                    'classified_c': qual_stats['classified_c'],
                    'classified_d': qual_stats['classified_d'],
                    'errors': qual_stats['errors'],
                    'duration_seconds': time.time() - step_start,
                }
                logger.info(
                    f"Qualification completed: "
                    f"A={qual_stats['classified_a']}, "
                    f"B={qual_stats['classified_b']}, "
                    f"C={qual_stats['classified_c']}, "
                    f"D={qual_stats['classified_d']}"
                )
            else:
                logger.info("STEP 3: Skipping qualification")
                results['steps']['qualification'] = {'skipped': True}

            # Step 4: Enrichment
            if not skip_enrichment and qualified_leads:
                logger.info("STEP 4: Enriching leads...")
                step_start = time.time()

                # Enrich C leads first (high priority)
                c_leads = [l for l in qualified_leads if l.classification.value == 'C']
                if c_leads:
                    logger.info(f"Enriching {len(c_leads)} C leads (high priority)")
                    self.enricher.enrich_batch(c_leads)

                # Enrich B leads (medium priority)
                b_leads = [l for l in qualified_leads if l.classification.value == 'B']
                if b_leads:
                    logger.info(f"Enriching {len(b_leads)} B leads (medium priority)")
                    self.enricher.enrich_batch(b_leads)

                # Update in database
                for lead in qualified_leads:
                    self.db.upsert_qualified_lead(lead)

                results['steps']['enrichment'] = {
                    'enriched_c': len(c_leads),
                    'enriched_b': len(b_leads),
                    'duration_seconds': time.time() - step_start,
                }
                logger.info("Enrichment completed")
            else:
                logger.info("STEP 4: Skipping enrichment")
                results['steps']['enrichment'] = {'skipped': True}

            # Step 5: Export
            if not skip_export:
                logger.info("STEP 5: Exporting results...")
                step_start = time.time()

                # Get all qualified leads for export
                all_qualified = []
                for cls in ['A', 'B', 'C']:
                    leads = self.db.get_leads_by_classification(
                        type('obj', (object,), {'value': cls})(),
                        limit=10000
                    )
                    all_qualified.extend(leads)

                # Export files
                export_files = {}

                # Leads A/B
                ab_leads = [l for l in all_qualified if l.classification.value in ['A', 'B']]
                if ab_leads:
                    export_files['leads_ab'] = self.excel_exporter.export_leads_ab(ab_leads)

                # Leads C
                c_leads = [l for l in all_qualified if l.classification.value == 'C']
                if c_leads:
                    export_files['leads_c'] = self.excel_exporter.export_leads_c(c_leads)

                # WhatsApp ready
                wa_leads = [l for l in ab_leads if l.whatsapp_ready]
                if wa_leads:
                    export_files['whatsapp'] = self.excel_exporter.export_whatsapp_ready(wa_leads)

                # Decision makers
                if ab_leads:
                    export_files['decision_makers'] = self.excel_exporter.export_decision_makers_report(ab_leads)

                results['steps']['export'] = {
                    'files': export_files,
                    'duration_seconds': time.time() - step_start,
                }
                logger.info(f"Export completed: {list(export_files.keys())}")
            else:
                logger.info("STEP 5: Skipping export")
                results['steps']['export'] = {'skipped': True}

            # Step 6: WhatsApp Preparation
            logger.info("STEP 6: Preparing WhatsApp contacts...")
            step_start = time.time()

            ab_leads = [l for l in all_qualified if l.classification.value in ['A', 'B']]
            wa_contacts = self.whatsapp_preparator.prepare_leads(ab_leads)

            if wa_contacts:
                wa_file = self.whatsapp_preparator.export_for_whatsapp_api(wa_contacts)
                results['steps']['whatsapp_prep'] = {
                    'contacts_prepared': len(wa_contacts),
                    'export_file': wa_file,
                    'duration_seconds': time.time() - step_start,
                }
            else:
                results['steps']['whatsapp_prep'] = {
                    'contacts_prepared': 0,
                    'duration_seconds': time.time() - step_start,
                }

            # Step 7: Email Preparation
            logger.info("STEP 7: Preparing email contacts...")
            step_start = time.time()

            email_contacts = self.email_preparator.prepare_leads(ab_leads)
            if email_contacts:
                email_contacts = self.email_preparator.get_sending_schedule(email_contacts)
                email_file = self.email_preparator.export_for_email_api(email_contacts)
                results['steps']['email_prep'] = {
                    'contacts_prepared': len(email_contacts),
                    'export_file': email_file,
                    'duration_seconds': time.time() - step_start,
                }
            else:
                results['steps']['email_prep'] = {
                    'contacts_prepared': 0,
                    'duration_seconds': time.time() - step_start,
                }

            # Step 8: Generate Reports
            logger.info("STEP 8: Generating reports...")
            step_start = time.time()

            report = self.report_generator.generate_daily_report(
                scraping_result=results['steps'].get('scraping', {}),
                qualification_result=results['steps'].get('qualification', {}),
                started_at=started_at,
            )

            # Export all reports
            report_files = self.report_generator.export_all_reports()

            results['steps']['reporting'] = {
                'report_file': report.report_file,
                'exported_files': report_files,
                'duration_seconds': time.time() - step_start,
            }
            logger.info("Reports generated")

            # Final summary
            duration = time.time() - start_time
            completed_at = datetime.utcnow()

            results['success'] = True
            results['completed_at'] = completed_at.isoformat()
            results['total_duration_seconds'] = duration

            logger.info("=" * 60)
            logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {duration:.1f}s")
            logger.info("=" * 60)
            logger.info(f"Summary:")
            logger.info(f"  Queries: {results['steps']['query_generation']['queries_generated']}")
            logger.info(f"  Scraped Leads: {results['steps']['scraping'].get('unique_leads', 'N/A')}")
            logger.info(f"  Qualified A: {results['steps']['qualification'].get('classified_a', 'N/A')}")
            logger.info(f"  Qualified B: {results['steps']['qualification'].get('classified_b', 'N/A')}")
            logger.info(f"  Qualified C: {results['steps']['qualification'].get('classified_c', 'N/A')}")
            logger.info(f"  WhatsApp Ready: {results['steps']['whatsapp_prep'].get('contacts_prepared', 'N/A')}")
            logger.info(f"  Email Ready: {results['steps']['email_prep'].get('contacts_prepared', 'N/A')}")

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            results['success'] = False
            results['errors'].append(str(e))
            results['completed_at'] = datetime.utcnow().isoformat()
            results['total_duration_seconds'] = time.time() - start_time

        return results

    def run_query_generation_only(self, priorities: List[int] = None, max_queries: int = None) -> dict:
        """Run only query generation."""
        queries = self.query_generator.generate_all_queries(
            priorities=priorities or [1, 2, 3],
            max_per_state=max_queries
        )

        if max_queries and len(queries) > max_queries:
            queries = queries[:max_queries]

        query_file = self.query_generator.save_queries(
            queries,
            f"queries_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        stats = self.query_generator.get_query_stats(queries)

        return {
            'success': True,
            'queries_generated': len(queries),
            'query_file': query_file,
            'stats': stats,
        }

    def run_scraping_only(self, queries: List[str] = None) -> dict:
        """Run only scraping."""
        if queries is None:
            # Use existing query file or generate new
            queries = self.query_generator.generate_all_queries(priorities=[1, 2])

        result = self.scraper_runner.run_full_scrape(queries=queries)

        return {
            'success': result.success,
            'total_queries': result.total_queries,
            'successful_queries': result.successful_queries,
            'total_results': result.total_results,
            'unique_leads': result.unique_leads,
            'duration_seconds': result.duration_seconds,
            'errors': result.errors,
        }

    def run_qualification_only(self, limit: int = 5000) -> dict:
        """Run only qualification on existing unqualified leads."""
        scraped_leads = self.db.get_unqualified_leads(limit=limit)

        if not scraped_leads:
            return {'success': True, 'message': 'No unqualified leads found', 'qualified': 0}

        leads_data = [lead.to_dict() for lead in scraped_leads]
        qualified = self.qualification_pipeline.qualify_batch(leads_data)

        # Save to database
        for lead in qualified:
            self.db.upsert_qualified_lead(lead)

        stats = self.qualification_pipeline.get_stats()

        return {
            'success': True,
            'processed': stats['total'],
            'classified_a': stats['classified_a'],
            'classified_b': stats['classified_b'],
            'classified_c': stats['classified_c'],
            'classified_d': stats['classified_d'],
        }

    def run_export_only(self) -> dict:
        """Run only export of existing qualified leads."""
        # Get all qualified leads
        all_qualified = []
        for cls in ['A', 'B', 'C']:
            leads = self.db.get_leads_by_classification(
                type('obj', (object,), {'value': cls})(),
                limit=10000
            )
            all_qualified.extend(leads)

        export_files = {}

        ab_leads = [l for l in all_qualified if l.classification.value in ['A', 'B']]
        if ab_leads:
            export_files['leads_ab'] = self.excel_exporter.export_leads_ab(ab_leads)

        c_leads = [l for l in all_qualified if l.classification.value == 'C']
        if c_leads:
            export_files['leads_c'] = self.excel_exporter.export_leads_c(c_leads)

        wa_leads = [l for l in ab_leads if l.whatsapp_ready]
        if wa_leads:
            export_files['whatsapp'] = self.excel_exporter.export_whatsapp_ready(wa_leads)

        if ab_leads:
            export_files['decision_makers'] = self.excel_exporter.export_decision_makers_report(ab_leads)

        # Generate reports
        report_files = self.report_generator.export_all_reports()
        export_files.update(report_files)

        return {
            'success': True,
            'exported_files': export_files,
            'leads_exported': {
                'A_B': len(ab_leads),
                'C': len(c_leads),
                'whatsapp_ready': len(wa_leads),
            }
        }

    def run_continuous(
        self,
        interval_hours: int = 24,
        max_runs: int = None,
        priorities: List[int] = None
    ) -> None:
        """Run continuous pipeline loop."""
        run_count = 0

        logger.info(f"Starting continuous mode: interval={interval_hours}h, max_runs={max_runs or 'unlimited'}")

        while max_runs is None or run_count < max_runs:
            logger.info(f"Continuous run #{run_count + 1}")

            try:
                result = self.run_full_pipeline(priorities=priorities)
                logger.info(f"Run #{run_count + 1} completed: success={result['success']}")
            except Exception as e:
                logger.error(f"Run #{run_count + 1} failed: {e}")

            run_count += 1

            if max_runs is None or run_count < max_runs:
                logger.info(f"Sleeping for {interval_hours} hours...")
                time.sleep(interval_hours * 3600)

        logger.info("Continuous mode completed")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Averta Lead Generation Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pipeline
  python -m src.main --full                              # Run complete pipeline
  python -m src.main --full --priorities 1 2             # Run with priorities 1 & 2
  python -m src.main --full --max-queries 100            # Limit queries for testing
  python -m src.main --generate-queries                  # Only generate queries
  python -m src.main --scrape                            # Only run scraper
  python -m src.main --qualify                           # Only qualify leads
  python -m src.main --export                            # Only export results
  python -m src.main --continuous --interval 24          # Run continuously every 24h

  # WhatsApp
  python -m src.main --whatsapp-campaign                 # Run WhatsApp campaign (dry run)
  python -m src.main --whatsapp-campaign --execute       # Actually send messages
  python -m src.main --whatsapp-test --lead-id LEAD_123  # Send test message
  python -m src.main --whatsapp-stats                    # Show campaign stats
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--full', action='store_true', help='Run complete pipeline')
    mode_group.add_argument('--generate-queries', action='store_true', help='Only generate queries')
    mode_group.add_argument('--scrape', action='store_true', help='Only run scraper')
    mode_group.add_argument('--qualify', action='store_true', help='Only qualify leads')
    mode_group.add_argument('--export', action='store_true', help='Only export results')
    mode_group.add_argument('--continuous', action='store_true', help='Run continuously')

    # WhatsApp modes
    mode_group.add_argument('--whatsapp-campaign', action='store_true', help='Run WhatsApp campaign')
    mode_group.add_argument('--whatsapp-test', action='store_true', help='Send test WhatsApp message')
    mode_group.add_argument('--whatsapp-stats', action='store_true', help='Show WhatsApp campaign stats')

    # Email modes
    mode_group.add_argument('--email-campaign', action='store_true', help='Run email campaign')
    mode_group.add_argument('--email-test', action='store_true', help='Send test email')
    mode_group.add_argument('--email-stats', action='store_true', help='Show email campaign stats')
    mode_group.add_argument('--email-prepare', action='store_true', help='Prepare and export email contacts')

    # Options
    parser.add_argument('--priorities', nargs='+', type=int, default=[1, 2],
                       help='State priorities to include (1=high, 2=medium, 3=low)')
    parser.add_argument('--max-queries', type=int, help='Maximum queries to generate')
    parser.add_argument('--max-leads', type=int, help='Maximum leads to process')
    parser.add_argument('--interval', type=int, default=24, help='Continuous mode interval in hours')
    parser.add_argument('--max-runs', type=int, help='Maximum runs in continuous mode')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--skip-scraping', action='store_true', help='Skip scraping step')
    parser.add_argument('--skip-qualification', action='store_true', help='Skip qualification step')
    parser.add_argument('--skip-enrichment', action='store_true', help='Skip enrichment step')
    parser.add_argument('--skip-export', action='store_true', help='Skip export step')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    # WhatsApp campaign options
    parser.add_argument('--execute', action='store_true', help='Execute campaign (not dry run)')
    parser.add_argument('--campaign-name', type=str, help='Campaign name')
    parser.add_argument('--classifications', nargs='+', type=str, help='Lead classifications (A, B, C)')
    parser.add_argument('--min-score', type=float, default=70, help='Minimum lead score')
    parser.add_argument('--max-messages', type=int, default=3, help='Max messages per lead')
    parser.add_argument('--segments', nargs='+', type=str, help='Filter by segments')
    parser.add_argument('--states', nargs='+', type=str, help='Filter by states (e.g., SP RJ MG)')

    # WhatsApp test options
    parser.add_argument('--lead-id', type=str, help='Lead ID for test message')
    parser.add_argument('--template', type=str, default='initial_contact', help='Template name')
    parser.add_argument('--custom-text', type=str, help='Custom message text')

    # Email campaign options
    parser.add_argument('--max-emails', type=int, default=4, help='Max emails per lead in sequence')
    parser.add_argument('--email-template', type=str, default='initial_outreach', help='Email template name')
    parser.add_argument('--sendgrid', action='store_true', help='Export for SendGrid format')
    parser.add_argument('--custom-subject', type=str, help='Custom email subject')
    parser.add_argument('--custom-html', type=str, help='Custom email HTML body')
    parser.add_argument('--custom-text-body', type=str, help='Custom email text body')

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize automation
    automation = LeadGenerationAutomation(config_path=args.config)

    try:
        if args.full:
            result = automation.run_full_pipeline(
                priorities=args.priorities,
                max_queries=args.max_queries,
                max_leads=args.max_leads,
                skip_scraping=args.skip_scraping,
                skip_qualification=args.skip_qualification,
                skip_enrichment=args.skip_enrichment,
                skip_export=args.skip_export,
            )
            sys.exit(0 if result['success'] else 1)

        elif args.generate_queries:
            result = automation.run_query_generation_only(
                priorities=args.priorities,
                max_queries=args.max_queries
            )
            print(f"Generated {result['queries_generated']} queries")
            print(f"Saved to: {result['query_file']}")

        elif args.scrape:
            result = automation.run_scraping_only()
            print(f"Scraping completed: {result['unique_leads']} unique leads")

        elif args.qualify:
            result = automation.run_qualification_only(limit=args.max_leads or 5000)
            print(f"Qualified {result.get('qualified', result.get('processed', 0))} leads")

        elif args.export:
            result = automation.run_export_only()
            print(f"Exported files: {list(result['exported_files'].keys())}")

        elif args.continuous:
            automation.run_continuous(
                interval_hours=args.interval,
                max_runs=args.max_runs,
                priorities=args.priorities
            )

        # WhatsApp commands
        elif args.whatsapp_campaign:
            result = automation.run_whatsapp_campaign(
                campaign_name=args.campaign_name,
                classifications=args.classifications,
                min_score=args.min_score,
                max_messages_per_lead=args.max_messages,
                segments=args.segments,
                states=args.states,
                dry_run=not args.execute,
            )
            print(f"Campaign: {result.get('campaign', result.get('campaign_name', 'N/A'))}")
            print(f"Leads found: {result.get('leads_found', 0)}")
            if result.get('dry_run'):
                print("DRY RUN - Use --execute to actually send messages")
                if result.get('leads_preview'):
                    print("\nPreview (first 10):")
                    for lead in result['leads_preview']:
                        print(f"  {lead['id']}: {lead['name']} ({lead['segment']}, {lead['city']}/{lead['state']}) - Score: {lead['score']} - Class: {lead['classification']} - DM: {lead['has_decision_maker']}")
            else:
                print(f"Messages sent: {result.get('results', {}).get('sent', 0)}")
                print(f"Failed: {result.get('results', {}).get('failed', 0)}")
                if result.get('results', {}).get('errors'):
                    print(f"Errors: {result['results']['errors'][:5]}")

        elif args.whatsapp_test:
            if not args.lead_id:
                print("Error: --lead-id is required for --whatsapp-test")
                sys.exit(1)

            result = automation.send_whatsapp_test(
                lead_id=args.lead_id,
                template_name=args.template,
                custom_text=args.custom_text,
            )
            if result.get('success'):
                print(f"Test message sent successfully!")
                print(f"External ID: {result.get('external_id')}")
            else:
                print(f"Failed to send test message: {result.get('error')}")
                sys.exit(1)

        elif args.whatsapp_stats:
            result = automation.get_whatsapp_campaign_stats()
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print("WhatsApp Campaign Stats:")
                for camp_id, stats in result.items():
                    print(f"  {camp_id}: {stats['name']}")
                    print(f"    Active: {stats['active']}")
                    print(f"    Sent: {stats['stats'].get('messages_sent', 0)}")
                    print(f"    Delivered: {stats['stats'].get('messages_delivered', 0)}")
                    print(f"    Read: {stats['stats'].get('messages_read', 0)}")
                    print(f"    Replies: {stats['stats'].get('replies_received', 0)}")
                    print(f"    Opt-outs: {stats['stats'].get('opt_outs', 0)}")
                    print(f"    Errors: {stats['stats'].get('errors', 0)}")

        # Email commands
        elif args.email_campaign:
            result = automation.run_email_campaign(
                campaign_name=args.campaign_name,
                classifications=args.classifications,
                min_score=args.min_score,
                max_emails_per_lead=args.max_emails,
                segments=args.segments,
                states=args.states,
                dry_run=not args.execute,
            )
            print(f"Campaign: {result.get('campaign', result.get('campaign_name', 'N/A'))}")
            print(f"Leads found: {result.get('leads_found', 0)}")
            if result.get('dry_run'):
                print("DRY RUN - Use --execute to actually send emails")
                if result.get('leads_preview'):
                    print("\nPreview (first 10):")
                    for lead in result['leads_preview']:
                        print(f"  {lead['id']}: {lead['name']} ({lead['segment']}, {lead['city']}/{lead['state']}) - Score: {lead['score']} - Class: {lead['classification']} - DM: {lead['has_decision_maker']}")
            else:
                print(f"Emails sent: {result.get('results', {}).get('sent', 0)}")
                print(f"Failed: {result.get('results', {}).get('failed', 0)}")
                if result.get('results', {}).get('errors'):
                    print(f"Errors: {result['results']['errors'][:5]}")

        elif args.email_test:
            if not args.lead_id:
                print("Error: --lead-id is required for --email-test")
                sys.exit(1)

            result = automation.send_email_test(
                lead_id=args.lead_id,
                template_name=args.email_template,
                custom_subject=args.custom_subject,
                custom_html=args.custom_html,
                custom_text=args.custom_text_body,
            )
            if result.get('success'):
                print(f"Test email sent successfully!")
                print(f"Provider: {result.get('provider')}")
                print(f"Message ID: {result.get('message_id')}")
            else:
                print(f"Failed to send test email: {result.get('error')}")
                sys.exit(1)

        elif args.email_stats:
            result = automation.get_email_campaign_stats()
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print("Email Campaign Stats:")
                for camp_id, stats in result.items():
                    print(f"  {camp_id}: {stats['name']}")
                    print(f"    Active: {stats['active']}")
                    print(f"    Sent: {stats['stats'].get('emails_sent', 0)}")
                    print(f"    Delivered: {stats['stats'].get('emails_delivered', 0)}")
                    print(f"    Opened: {stats['stats'].get('emails_opened', 0)}")
                    print(f"    Clicked: {stats['stats'].get('emails_clicked', 0)}")
                    print(f"    Replied: {stats['stats'].get('replies_received', 0)}")
                    print(f"    Unsubscribed: {stats['stats'].get('unsubscribed', 0)}")
                    print(f"    Bounced: {stats['stats'].get('bounced', 0)}")
                    print(f"    Errors: {stats['stats'].get('errors', 0)}")

        elif args.email_prepare:
            result = automation.prepare_email_contacts(
                classifications=args.classifications,
                min_score=args.min_score,
                segments=args.segments,
                states=args.states,
                export_csv=True,
                export_sendgrid=args.sendgrid,
            )
            if result.get('success'):
                print(f"Contacts prepared: {result.get('contacts_prepared', 0)}")
                if result.get('export_files'):
                    for fmt, path in result['export_files'].items():
                        print(f"  {fmt.upper()} export: {path}")
                if result.get('stats'):
                    stats = result['stats']
                    print(f"\nStats:")
                    print(f"  Total: {stats.get('total', 0)}")
                    print(f"  Avg Score: {stats.get('avg_score', 0):.1f}")
                    print(f"  With Decision Maker: {stats.get('with_decision_maker', 0)}")
                    print(f"  With Direct Email: {stats.get('with_direct_email', 0)}")
                    print(f"  By Classification: {stats.get('by_classification', {})}")
                    print(f"  By Template: {stats.get('by_template', {})}")
            else:
                print(f"Error: {result.get('error')}")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Automation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()