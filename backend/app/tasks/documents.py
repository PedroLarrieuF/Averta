"""Document processing tasks: XML parsing, validation, discrepancy detection"""
from celery import Task
from app.core.celery_app import celery_app
from app.core.config import settings
import structlog
import asyncio

logger = structlog.get_logger()


class AsyncTask(Task):
    """Base task with async support"""
    def __call__(self, *args, **kwargs):
        return asyncio.run(self.run_async(*args, **kwargs))

    async def run_async(self, *args, **kwargs):
        raise NotImplementedError


@celery_app.task(base=AsyncTask, bind=True, max_retries=3, default_retry_delay=60)
async def process_document(self, document_id: str):
    """Process uploaded document: parse XML/PDF, extract data, run rules"""
    from app.core.database import get_prisma
    from app.services.xml_parser import parse_cte_xml, parse_nfe_xml
    from app.services.rules_engine import run_rules

    db = await get_prisma()

    try:
        # Update status to processing
        await db.document.update(
            where={"id": document_id},
            data={"status": "PROCESSING"},
        )

        doc = await db.document.find_unique(where={"id": document_id})
        if not doc:
            logger.error("document_not_found", document_id=document_id)
            return

        # Download from S3/MinIO
        from app.services.storage import download_file
        xml_content = await download_file(doc.s3Bucket, doc.s3Key)

        # Parse based on type
        parsed_data = None
        if doc.type == "CTE":
            parsed_data = await parse_cte_xml(xml_content)
        elif doc.type == "NFE":
            parsed_data = await parse_nfe_xml(xml_content)
        else:
            raise ValueError(f"Unsupported document type: {doc.type}")

        # Update document with parsed data
        await db.document.update(
            where={"id": document_id},
            data={
                "parsedData": parsed_data,
                "rawXml": xml_content[:100000] if xml_content else None,  # Store first 100KB
                "accessKey": parsed_data.get("access_key"),
                "issueDate": parsed_data.get("issue_date"),
                "totalValue": parsed_data.get("total_value"),
                "freightValue": parsed_data.get("freight_value"),
                "icmsValue": parsed_data.get("icms_value"),
                "weight": parsed_data.get("weight"),
                "volume": parsed_data.get("volume"),
                "status": "PROCESSED",
                "processedAt": "now()",
            },
        )

        # Run discrepancy detection rules
        await run_rules.delay(document_id, parsed_data, doc.companyId, doc.clientId)

        logger.info("document_processed", document_id=document_id, type=doc.type)

    except Exception as e:
        logger.exception("document_processing_failed", document_id=document_id, error=str(e))
        await db.document.update(
            where={"id": document_id},
            data={
                "status": "FAILED",
                "errorMessage": str(e)[:500],
            },
        )
        raise


@celery_app.task(base=AsyncTask, bind=True)
async def check_stale_documents(self):
    """Check for documents stuck in PROCESSING state"""
    from app.core.database import get_prisma
    from datetime import datetime, timedelta

    db = await get_prisma()
    stale_threshold = datetime.utcnow() - timedelta(minutes=10)

    stale_docs = await db.document.find_many(
        where={
            "status": "PROCESSING",
            "updatedAt": {"lt": stale_threshold},
        }
    )

    for doc in stale_docs:
        logger.warning("stale_document_found", document_id=doc.id)
        await process_document.delay(doc.id)


@celery_app.task(base=AsyncTask, bind=True)
async def reprocess_document(self, document_id: str):
    """Reprocess a document (e.g., after rules update)"""
    from app.core.database import get_prisma

    db = await get_prisma()
    await db.document.update(
        where={"id": document_id},
        data={"status": "UPLOADED"},
    )
    await process_document.delay(document_id)


@celery_app.task(base=AsyncTask, bind=True)
async def batch_process_documents(self, document_ids: list[str]):
    """Process multiple documents in batch"""
    for doc_id in document_ids:
        process_document.delay(doc_id)