"""Master database for persistent lead storage."""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import os
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import json

from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, DateTime,
    Date, Text, Index, ForeignKey, UniqueConstraint, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError

from utils.config_loader import get_settings
from utils.logging import get_logger
from .models import (
    ScrapedLead, QualifiedLead, DecisionMaker, InstitutionalContact,
    ScrapingJob, DailyReport, LeadClassification, ContactType, EnrichmentStatus
)

logger = get_logger(__name__)

Base = declarative_base()


class ScrapedLeadModel(Base):
    """Scraped lead database model."""
    __tablename__ = 'scraped_leads'

    id = Column(String(32), primary_key=True)
    place_id = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(500), nullable=True)
    trade_name = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    street = Column(String(500), nullable=True)
    number = Column(String(50), nullable=True)
    complement = Column(String(200), nullable=True)
    neighborhood = Column(String(200), nullable=True)
    city = Column(String(200), index=True, nullable=True)
    state = Column(String(2), index=True, nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), default='Brasil')
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String(50), nullable=True)
    phone_verified = Column(Boolean, default=False)
    whatsapp = Column(String(50), nullable=True)
    whatsapp_verified = Column(Boolean, default=False)
    email = Column(String(200), nullable=True)
    email_verified = Column(Boolean, default=False)
    website = Column(String(500), nullable=True)
    website_verified = Column(Boolean, default=False)
    linkedin = Column(String(500), nullable=True)
    linkedin_verified = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)
    reviews_count = Column(Integer, nullable=True)
    price_level = Column(Integer, nullable=True)
    categories = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    opening_hours = Column(JSON, nullable=True)
    permanently_closed = Column(Boolean, default=False)
    temporarily_closed = Column(Boolean, default=False)
    photos = Column(JSON, nullable=True)
    reviews = Column(JSON, nullable=True)
    emails_from_website = Column(JSON, nullable=True)
    social_media = Column(JSON, nullable=True)
    source_query = Column(String(500), index=True, nullable=True)
    scraped_at = Column(DateTime, index=True, default=datetime.utcnow)
    raw_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    qualified_lead = relationship("QualifiedLeadModel", back_populates="scraped_lead", uselist=False)

    __table_args__ = (
        Index('idx_scraped_city_state', 'city', 'state'),
        Index('idx_scraped_name_city', 'name', 'city'),
    )


class QualifiedLeadModel(Base):
    """Qualified lead database model."""
    __tablename__ = 'qualified_leads'

    id = Column(String(32), primary_key=True)
    scraped_lead_id = Column(String(32), ForeignKey('scraped_leads.id'), unique=True, index=True, nullable=True)
    name = Column(String(500), nullable=True)
    trade_name = Column(String(500), nullable=True)
    segment = Column(String(200), index=True, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(200), index=True, nullable=True)
    state = Column(String(2), index=True, nullable=True)
    postal_code = Column(String(20), nullable=True)
    phone = Column(String(50), nullable=True)
    phone_verified = Column(Boolean, default=False)
    whatsapp = Column(String(50), nullable=True)
    whatsapp_verified = Column(Boolean, default=False)
    email = Column(String(200), nullable=True)
    email_verified = Column(Boolean, default=False)
    website = Column(String(500), nullable=True)
    website_verified = Column(Boolean, default=False)
    linkedin = Column(String(500), nullable=True)
    linkedin_verified = Column(Boolean, default=False)
    rating = Column(Float, nullable=True)
    reviews_count = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    score = Column(Float, default=0.0, index=True)
    classification = Column(String(1), index=True, default='D')
    operational_fit_score = Column(Float, default=0.0)
    commercial_fit_score = Column(Float, default=0.0)
    data_confidence_score = Column(Float, default=0.0)
    decision_makers_json = Column(JSON, nullable=True)
    institutional_contacts_json = Column(JSON, nullable=True)
    source_query = Column(String(500), index=True, nullable=True)
    scraped_at = Column(DateTime, nullable=True)
    qualified_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    enrichment_status = Column(String(20), default='pending')
    enrichment_priority = Column(String(10), default='low')
    notes = Column(Text, nullable=True)
    whatsapp_ready = Column(Boolean, default=False)
    whatsapp_template_suggested = Column(String(500), nullable=True)
    whatsapp_opt_in_status = Column(String(20), default='unknown')
    whatsapp_last_contact_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scraped_lead = relationship("ScrapedLeadModel", back_populates="qualified_lead")
    decision_makers = relationship("DecisionMakerModel", back_populates="lead", cascade="all, delete-orphan")
    institutional_contacts = relationship("InstitutionalContactModel", back_populates="lead", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_qualified_classification_score', 'classification', 'score'),
        Index('idx_qualified_city_state_class', 'city', 'state', 'classification'),
        Index('idx_qualified_segment_class', 'segment', 'classification'),
        Index('idx_qualified_whatsapp_ready', 'whatsapp_ready'),
    )


class DecisionMakerModel(Base):
    """Decision maker database model."""
    __tablename__ = 'decision_makers'

    id = Column(String(32), primary_key=True)
    lead_id = Column(String(32), ForeignKey('qualified_leads.id'), index=True, nullable=False)
    name = Column(String(300), nullable=True)
    role = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    email_verified = Column(Boolean, default=False)
    phone = Column(String(50), nullable=True)
    phone_verified = Column(Boolean, default=False)
    whatsapp = Column(String(50), nullable=True)
    whatsapp_verified = Column(Boolean, default=False)
    linkedin = Column(String(500), nullable=True)
    linkedin_verified = Column(Boolean, default=False)
    source = Column(String(100), default='unknown')
    source_url = Column(String(500), nullable=True)
    confidence = Column(Float, default=0.0)
    identified_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("QualifiedLeadModel", back_populates="decision_makers")


class InstitutionalContactModel(Base):
    """Institutional contact database model."""
    __tablename__ = 'institutional_contacts'

    id = Column(String(32), primary_key=True)
    lead_id = Column(String(32), ForeignKey('qualified_leads.id'), index=True, nullable=False)
    contact_type = Column(String(50), default='unknown')
    value = Column(String(500), nullable=False)
    label = Column(String(200), nullable=True)
    verified = Column(Boolean, default=False)
    source = Column(String(100), default='unknown')
    source_url = Column(String(500), nullable=True)
    confidence = Column(Float, default=0.0)
    identified_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lead = relationship("QualifiedLeadModel", back_populates="institutional_contacts")


class ScrapingJobModel(Base):
    """Scraping job database model."""
    __tablename__ = 'scraping_jobs'

    id = Column(String(32), primary_key=True)
    query = Column(String(500), index=True, nullable=False)
    status = Column(String(20), default='pending', index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    results_count = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    output_file = Column(String(500), nullable=True)
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_job_status_date', 'status', 'created_at'),
    )


class DailyReportModel(Base):
    """Daily report database model."""
    __tablename__ = 'daily_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, unique=True, index=True, nullable=False)
    queries_executed = Column(Integer, default=0)
    companies_found = Column(Integer, default=0)
    unique_companies = Column(Integer, default=0)
    leads_classified_a = Column(Integer, default=0)
    leads_classified_b = Column(Integer, default=0)
    leads_classified_c = Column(Integer, default=0)
    leads_classified_d = Column(Integer, default=0)
    leads_discarded = Column(Integer, default=0)
    decision_makers_identified = Column(Integer, default=0)
    institutional_contacts_valid = Column(Integer, default=0)
    business_phones_valid = Column(Integer, default=0)
    corporate_emails_found = Column(Integer, default=0)
    linkedin_verified = Column(Integer, default=0)
    states_covered = Column(Integer, default=0)
    segments_covered = Column(Integer, default=0)
    cost_per_qualified_lead = Column(Float, default=0.0)
    qualification_rate = Column(Float, default=0.0)
    leads_ab_file = Column(String(500), nullable=True)
    leads_c_file = Column(String(500), nullable=True)
    report_file = Column(String(500), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    errors = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MasterDatabase:
    """Master database manager."""

    def __init__(self, db_path: Optional[str] = None):
        settings = get_settings()
        self.db_path = db_path or settings.master_db
        self.engine = None
        self.SessionLocal = None
        self._init_db()

    def _init_db(self):
        """Initialize database connection and create tables."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            echo=False,
            pool_pre_ping=True,
            connect_args={'check_same_thread': False}
        )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Create tables
        Base.metadata.create_all(bind=self.engine)

        logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_session(self) -> Session:
        """Get database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_session_direct(self) -> Session:
        """Get a session directly (caller must manage commit/close)."""
        return self.SessionLocal()

    # ============================================
    # Scraped Leads Operations
    # ============================================

    def upsert_scraped_lead(self, lead: ScrapedLead) -> ScrapedLeadModel:
        """Insert or update scraped lead."""
        with self.get_session() as session:
            # Check if exists by place_id
            existing = None
            if lead.place_id:
                existing = session.query(ScrapedLeadModel).filter(
                    ScrapedLeadModel.place_id == lead.place_id
                ).first()

            if not existing and lead.name and lead.city and lead.state:
                # Try to find by name + city + state
                existing = session.query(ScrapedLeadModel).filter(
                    ScrapedLeadModel.name == lead.name,
                    ScrapedLeadModel.city == lead.city,
                    ScrapedLeadModel.state == lead.state
                ).first()

            if existing:
                # Update existing
                lead.id = existing.id
                for key, value in lead.to_dict().items():
                    if key != 'id' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                session.flush()
                return existing
            else:
                # Insert new
                if not lead.id:
                    lead.id = f"sl_{datetime.utcnow().timestamp()}"

                model = ScrapedLeadModel(**lead.to_dict())
                model.id = lead.id
                session.add(model)
                session.flush()
                return model

    def get_scraped_lead(self, lead_id: str) -> Optional[ScrapedLeadModel]:
        """Get scraped lead by ID."""
        with self.get_session() as session:
            return session.query(ScrapedLeadModel).filter(
                ScrapedLeadModel.id == lead_id
            ).first()

    def get_scraped_lead_by_place_id(self, place_id: str) -> Optional[ScrapedLeadModel]:
        """Get scraped lead by Google Place ID."""
        with self.get_session() as session:
            return session.query(ScrapedLeadModel).filter(
                ScrapedLeadModel.place_id == place_id
            ).first()

    def get_unqualified_leads(self, limit: int = 1000) -> List[ScrapedLeadModel]:
        """Get leads that haven't been qualified yet."""
        with self.get_session() as session:
            return session.query(ScrapedLeadModel).outerjoin(
                QualifiedLeadModel,
                ScrapedLeadModel.id == QualifiedLeadModel.scraped_lead_id
            ).filter(
                QualifiedLeadModel.id.is_(None)
            ).limit(limit).all()

    # ============================================
    # Qualified Leads Operations
    # ============================================

    def upsert_qualified_lead(self, lead: QualifiedLead) -> QualifiedLeadModel:
        """Insert or update qualified lead."""
        with self.get_session() as session:
            # Check if exists by scraped_lead_id
            existing = None
            if lead.scraped_lead_id:
                existing = session.query(QualifiedLeadModel).filter(
                    QualifiedLeadModel.scraped_lead_id == lead.scraped_lead_id
                ).first()

            if not existing and lead.name and lead.city and lead.state:
                # Try to find by name + city + state
                existing = session.query(QualifiedLeadModel).filter(
                    QualifiedLeadModel.name == lead.name,
                    QualifiedLeadModel.city == lead.city,
                    QualifiedLeadModel.state == lead.state
                ).first()

            lead_dict = lead.to_dict()
            decision_makers = lead_dict.pop('decision_makers', [])
            institutional_contacts = lead_dict.pop('institutional_contacts', [])

            if existing:
                # Update existing
                lead.id = existing.id
                for key, value in lead_dict.items():
                    if key != 'id' and hasattr(existing, key):
                        setattr(existing, key, value)
                existing.last_updated = datetime.utcnow()

                # Update decision makers
                self._sync_decision_makers(session, existing.id, decision_makers)
                # Update institutional contacts
                self._sync_institutional_contacts(session, existing.id, institutional_contacts)

                session.flush()
                return existing
            else:
                # Insert new
                if not lead.id:
                    lead.id = f"ql_{datetime.utcnow().timestamp()}"

                model = QualifiedLeadModel(**lead_dict)
                model.id = lead.id
                session.add(model)
                session.flush()

                # Add decision makers
                for dm in decision_makers:
                    dm_model = DecisionMakerModel(**dm)
                    dm_model.lead_id = model.id
                    session.add(dm_model)

                # Add institutional contacts
                for ic in institutional_contacts:
                    ic_model = InstitutionalContactModel(**ic)
                    ic_model.lead_id = model.id
                    session.add(ic_model)

                session.flush()
                return model

    def _sync_decision_makers(self, session: Session, lead_id: str, decision_makers: List[Dict]):
        """Sync decision makers for a lead."""
        # Delete existing
        session.query(DecisionMakerModel).filter(
            DecisionMakerModel.lead_id == lead_id
        ).delete()

        # Add new
        for dm in decision_makers:
            dm_model = DecisionMakerModel(**dm)
            dm_model.lead_id = lead_id
            session.add(dm_model)

    def _sync_institutional_contacts(self, session: Session, lead_id: str, contacts: List[Dict]):
        """Sync institutional contacts for a lead."""
        # Delete existing
        session.query(InstitutionalContactModel).filter(
            InstitutionalContactModel.lead_id == lead_id
        ).delete()

        # Add new
        for ic in contacts:
            ic_model = InstitutionalContactModel(**ic)
            ic_model.lead_id = lead_id
            session.add(ic_model)

    def get_qualified_lead(self, lead_id: str) -> Optional[QualifiedLead]:
        """Get qualified lead by ID with relations."""
        with self.get_session() as session:
            model = session.query(QualifiedLeadModel).filter(
                QualifiedLeadModel.id == lead_id
            ).first()

            if not model:
                return None

            return self._model_to_qualified_lead(model)

    def _model_to_qualified_lead(self, model: QualifiedLeadModel) -> QualifiedLead:
        """Convert model to QualifiedLead dataclass."""
        lead = QualifiedLead()

        # Simple fields
        for key in QualifiedLead.__dataclass_fields__.keys():
            if key in ['decision_makers', 'institutional_contacts']:
                continue
            if hasattr(model, key):
                value = getattr(model, key)
                if key == 'classification' and value:
                    setattr(lead, key, LeadClassification(value))
                elif key == 'enrichment_status' and value:
                    setattr(lead, key, EnrichmentStatus(value))
                else:
                    setattr(lead, key, value)

        # Decision makers
        for dm_model in model.decision_makers:
            dm = DecisionMaker(
                id=dm_model.id,
                lead_id=dm_model.lead_id,
                name=dm_model.name,
                role=dm_model.role,
                department=dm_model.department,
                email=dm_model.email,
                email_verified=dm_model.email_verified,
                phone=dm_model.phone,
                phone_verified=dm_model.phone_verified,
                whatsapp=dm_model.whatsapp,
                whatsapp_verified=dm_model.whatsapp_verified,
                linkedin=dm_model.linkedin,
                linkedin_verified=dm_model.linkedin_verified,
                source=dm_model.source,
                source_url=dm_model.source_url,
                confidence=dm_model.confidence,
                identified_at=dm_model.identified_at,
                notes=dm_model.notes,
            )
            lead.decision_makers.append(dm)

        # Institutional contacts
        for ic_model in model.institutional_contacts:
            ic = InstitutionalContact(
                id=ic_model.id,
                lead_id=ic_model.lead_id,
                contact_type=ContactType(ic_model.contact_type),
                value=ic_model.value,
                label=ic_model.label,
                verified=ic_model.verified,
                source=ic_model.source,
                source_url=ic_model.source_url,
                confidence=ic_model.confidence,
                identified_at=ic_model.identified_at,
                notes=ic_model.notes,
            )
            lead.institutional_contacts.append(ic)

        return lead

    def get_leads_by_classification(self, classification: LeadClassification,
                                     limit: int = 1000, offset: int = 0) -> List[QualifiedLead]:
        """Get leads by classification."""
        with self.get_session() as session:
            models = session.query(QualifiedLeadModel).filter(
                QualifiedLeadModel.classification == classification.value
            ).order_by(
                QualifiedLeadModel.score.desc()
            ).offset(offset).limit(limit).all()

            return [self._model_to_qualified_lead(m) for m in models]

    def get_leads_for_export(self, classifications: List[LeadClassification] = None,
                              limit: int = None) -> List[QualifiedLead]:
        """Get leads for export (A and B by default)."""
        if classifications is None:
            classifications = [LeadClassification.A, LeadClassification.B]

        with self.get_session() as session:
            query = session.query(QualifiedLeadModel).filter(
                QualifiedLeadModel.classification.in_([c.value for c in classifications])
            ).order_by(
                QualifiedLeadModel.score.desc(),
                QualifiedLeadModel.qualified_at.desc()
            )

            if limit:
                query = query.limit(limit)

            models = query.all()
            return [self._model_to_qualified_lead(m) for m in models]

    def get_leads_for_whatsapp(self, limit: int = None) -> List[QualifiedLead]:
        """Get leads ready for WhatsApp."""
        with self.get_session() as session:
            query = session.query(QualifiedLeadModel).filter(
                QualifiedLeadModel.whatsapp_ready == True,
                QualifiedLeadModel.classification.in_(['A', 'B'])
            ).order_by(
                QualifiedLeadModel.score.desc()
            )

            if limit:
                query = query.limit(limit)

            models = query.all()
            return [self._model_to_qualified_lead(m) for m in models]

    def count_leads_by_classification(self) -> Dict[str, int]:
        """Count leads by classification."""
        with self.get_session() as session:
            from sqlalchemy import func
            results = session.query(
                QualifiedLeadModel.classification,
                func.count(QualifiedLeadModel.id)
            ).group_by(QualifiedLeadModel.classification).all()

            return {r[0]: r[1] for r in results}

    def get_coverage_stats(self) -> Dict[str, Any]:
        """Get coverage statistics."""
        with self.get_session() as session:
            from sqlalchemy import func, distinct

            stats = {}

            # Total leads
            stats['total_qualified'] = session.query(func.count(QualifiedLeadModel.id)).scalar()

            # By state
            state_results = session.query(
                QualifiedLeadModel.state,
                func.count(QualifiedLeadModel.id)
            ).group_by(QualifiedLeadModel.state).all()
            stats['by_state'] = {r[0]: r[1] for r in state_results if r[0]}

            # By segment
            segment_results = session.query(
                QualifiedLeadModel.segment,
                func.count(QualifiedLeadModel.id)
            ).group_by(QualifiedLeadModel.segment).all()
            stats['by_segment'] = {r[0]: r[1] for r in segment_results if r[0]}

            # By classification
            stats['by_classification'] = self.count_leads_by_classification()

            # Contacts
            stats['with_email'] = session.query(func.count(QualifiedLeadModel.id)).filter(
                QualifiedLeadModel.email.isnot(None),
                QualifiedLeadModel.email != ''
            ).scalar()

            stats['with_phone'] = session.query(func.count(QualifiedLeadModel.id)).filter(
                QualifiedLeadModel.phone.isnot(None),
                QualifiedLeadModel.phone != ''
            ).scalar()

            stats['with_whatsapp'] = session.query(func.count(QualifiedLeadModel.id)).filter(
                QualifiedLeadModel.whatsapp.isnot(None),
                QualifiedLeadModel.whatsapp != ''
            ).scalar()

            stats['with_linkedin'] = session.query(func.count(QualifiedLeadModel.id)).filter(
                QualifiedLeadModel.linkedin.isnot(None),
                QualifiedLeadModel.linkedin != ''
            ).scalar()

            stats['whatsapp_ready'] = session.query(func.count(QualifiedLeadModel.id)).filter(
                QualifiedLeadModel.whatsapp_ready == True
            ).scalar()

            return stats

    # ============================================
    # Scraping Jobs Operations
    # ============================================

    def create_scraping_job(self, job: ScrapingJob) -> ScrapingJobModel:
        """Create scraping job record."""
        with self.get_session() as session:
            model = ScrapingJobModel(**job.to_dict())
            model.id = job.id
            session.add(model)
            session.flush()
            return model

    def update_scraping_job(self, job_id: str, **kwargs) -> Optional[ScrapingJobModel]:
        """Update scraping job."""
        with self.get_session() as session:
            model = session.query(ScrapingJobModel).filter(
                ScrapingJobModel.id == job_id
            ).first()

            if model:
                for key, value in kwargs.items():
                    if hasattr(model, key):
                        setattr(model, key, value)
                model.updated_at = datetime.utcnow()
                session.flush()

            return model

    def get_scraping_job(self, job_id: str) -> Optional[ScrapingJobModel]:
        """Get scraping job by ID."""
        with self.get_session() as session:
            return session.query(ScrapingJobModel).filter(
                ScrapingJobModel.id == job_id
            ).first()

    def get_pending_jobs(self, limit: int = 100) -> List[ScrapingJobModel]:
        """Get pending scraping jobs."""
        with self.get_session() as session:
            return session.query(ScrapingJobModel).filter(
                ScrapingJobModel.status == 'pending'
            ).order_by(ScrapingJobModel.created_at).limit(limit).all()

    # ============================================
    # Daily Reports Operations
    # ============================================

    def upsert_daily_report(self, report: DailyReport) -> DailyReportModel:
        """Insert or update daily report."""
        with self.get_session() as session:
            existing = session.query(DailyReportModel).filter(
                DailyReportModel.report_date == report.date
            ).first()

            report_dict = report.to_dict()

            if existing:
                for key, value in report_dict.items():
                    if key != 'id' and hasattr(existing, key):
                        setattr(existing, key, value)
                session.flush()
                return existing
            else:
                model = DailyReportModel(**report_dict)
                session.add(model)
                session.flush()
                return model

    def get_daily_report(self, report_date: date) -> Optional[DailyReportModel]:
        """Get daily report by date."""
        with self.get_session() as session:
            return session.query(DailyReportModel).filter(
                DailyReportModel.report_date == report_date
            ).first()

    def get_recent_reports(self, days: int = 30) -> List[DailyReportModel]:
        """Get recent daily reports."""
        from datetime import timedelta
        cutoff = date.today() - timedelta(days=days)

        with self.get_session() as session:
            return session.query(DailyReportModel).filter(
                DailyReportModel.report_date >= cutoff
            ).order_by(DailyReportModel.report_date.desc()).all()


# Global instance
_master_db: Optional[MasterDatabase] = None


def get_master_db() -> MasterDatabase:
    """Get global master database instance."""
    global _master_db
    if _master_db is None:
        _master_db = MasterDatabase()
    return _master_db


def init_master_db(db_path: Optional[str] = None) -> MasterDatabase:
    """Initialize master database."""
    global _master_db
    _master_db = MasterDatabase(db_path)
    return _master_db