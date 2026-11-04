"""Reports module service"""

from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import openpyxl
import structlog
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.core.dependencies import PaginationParams
from app.core.exceptions import BadRequestError
from app.modules.contracts.service import ContractsService
from app.modules.reports.schemas import (
    DashboardKPIs,
    DiscrepancyStats,
    ExportRequest,
    ExportResponse,
    RecoveryReport,
    RecoveryReportItem,
    SuccessFeeReport,
    SuccessFeeReportItem,
)
from app.services.storage import get_presigned_url, upload_file
from prisma import Prisma

logger = structlog.get_logger()

# Constants
PROGRESSIVE_MONTH_DAYS = 30


class ReportsService:
    def __init__(self, db: Prisma):
        self.db = db
        self.contracts_service = ContractsService(db)

    # ============================================
    # DASHBOARD KPIs
    # ============================================

    async def get_dashboard_kpis(self, company_id: str) -> DashboardKPIs:
        """Get main dashboard KPIs"""
        now = datetime.utcnow()

        # Total recoverable (sum of contest expected values)
        contests = await self.db.contest.find_many(
            where={"companyId": company_id},
            include={"items": True},
        )

        total_recoverable = sum(c.totalExpected for c in contests)
        total_recovered = sum(c.totalRecovered for c in contests)
        active_contests = sum(
            1 for c in contests if c.status in ["DRAFT", "SENT", "ACKNOWLEDGED", "NEGOTIATING"]
        )

        recovery_rate = (total_recovered / total_recoverable * 100) if total_recoverable > 0 else 0

        # Discrepancies for conversion rate
        discrepancies = await self.db.discrepancy.find_many(
            where={"companyId": company_id},
        )
        total_detected = len(discrepancies)
        total_approved = sum(
            1 for d in discrepancies if d.status in ["APPROVED", "CONTESTED", "RECOVERED"]
        )
        conversion_rate = (total_approved / total_detected * 100) if total_detected > 0 else 0

        # Avg recovery time
        resolved = [c for c in contests if c.resolvedAt and c.createdAt]
        avg_days = 0
        if resolved:
            avg_days = sum((c.resolvedAt - c.createdAt).days for c in resolved) / len(resolved)

        # Top carriers by volume
        carrier_volumes = defaultdict(float)
        for c in contests:
            carrier_volumes[c.carrierId] += c.totalExpected

        carrier_names = {}
        if carrier_volumes:
            carriers = await self.db.carrier.find_many(
                where={"id": {"in": list(carrier_volumes.keys())}}
            )
            carrier_names = {c.id: c.name for c in carriers}

        top_carriers = [
            {"carrier_id": cid, "carrier_name": carrier_names.get(cid, "N/A"), "volume": vol}
            for cid, vol in sorted(carrier_volumes.items(), key=lambda x: x[1], reverse=True)[:10]
        ]

        # Top discrepancy types
        disc_types = defaultdict(lambda: {"count": 0, "value": 0})
        for d in discrepancies:
            disc_types[d.type]["count"] += 1
            disc_types[d.type]["value"] += d.difference

        top_disc_types = [
            {"type": k, "count": v["count"], "value": v["value"]}
            for k, v in sorted(disc_types.items(), key=lambda x: x[1]["value"], reverse=True)[:10]
        ]

        # Monthly trend (last 12 months)
        monthly = []
        for i in range(11, -1, -1):
            month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            month_contests = [c for c in contests if month_start <= c.createdAt <= month_end]
            month_recovered = sum(c.totalRecovered for c in month_contests)
            month_expected = sum(c.totalExpected for c in month_contests)

            monthly.append(
                {
                    "month": month_start.strftime("%Y-%m"),
                    "expected": month_expected,
                    "recovered": month_recovered,
                    "contests": len(month_contests),
                }
            )

        return DashboardKPIs(
            total_recoverable=total_recoverable,
            total_recovered=total_recovered,
            recovery_rate=round(recovery_rate, 2),
            total_contests=len(contests),
            active_contests=active_contests,
            conversion_rate=round(conversion_rate, 2),
            avg_recovery_time_days=round(avg_days, 1),
            top_carriers_by_volume=top_carriers,
            top_discrepancy_types=top_disc_types,
            monthly_trend=monthly,
        )

    # ============================================
    # RECOVERY REPORT
    # ============================================

    async def get_recovery_report(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        client_id: str | None = None,
        carrier_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        status: list[str] | None = None,
    ) -> RecoveryReport:
        """Get detailed recovery report"""
        where = {"companyId": company_id}
        if client_id:
            where["clientId"] = client_id
        if carrier_id:
            where["carrierId"] = carrier_id
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to
        if status:
            where["status"] = {"in": status}

        # Get total count
        total = await self.db.contest.count(where=where)

        # Get paginated contests
        contests = await self.db.contest.find_many(
            where=where,
            skip=pagination.offset,
            take=pagination.limit,
            order={"createdAt": "desc"},
            include={"client": True, "carrier": True, "contract": True},
        )

        items = []
        for c in contests:
            # Get pricing model info
            pricing_model = "FIXED"
            progressive_month = None
            if c.contractId:
                contract = await self.db.contract.find_unique(where={"id": c.contractId})
                if contract:
                    pricing_model = contract.pricingModel
                    if contract.pricingModel == "PROGRESSIVE":
                        start_date = contract.progressiveStartDate or contract.startDate
                        check_date = datetime.utcnow()
                        days_diff = (check_date - start_date).days
                        progressive_month = (
                            1
                            if days_diff < PROGRESSIVE_MONTH_DAYS
                            else (days_diff // PROGRESSIVE_MONTH_DAYS) + 1
                        )

            items.append(
                RecoveryReportItem(
                    contest_id=c.id,
                    contest_number=c.number,
                    client_name=c.client.name if c.client else "N/A",
                    carrier_name=c.carrier.name if c.carrier else "N/A",
                    contract_number=c.contract.number if c.contract else None,
                    status=c.status,
                    total_expected=c.totalExpected,
                    total_recovered=c.totalRecovered,
                    success_fee_pct=c.successFeePct,
                    success_fee_value=c.successFeeValue,
                    net_recovery=c.netRecovery,
                    created_at=c.createdAt,
                    resolved_at=c.resolvedAt,
                    pricing_model=pricing_model,
                    progressive_month=progressive_month,
                )
            )

        # Summary
        all_contests = await self.db.contest.find_many(where=where)
        summary = {
            "total_expected": sum(c.totalExpected for c in all_contests),
            "total_recovered": sum(c.totalRecovered for c in all_contests),
            "total_success_fee": sum(c.successFeeValue for c in all_contests),
            "total_net_recovery": sum(c.netRecovery for c in all_contests),
            "by_status": {},
        }
        for c in all_contests:
            summary["by_status"][c.status] = summary["by_status"].get(c.status, 0) + 1

        return RecoveryReport(
            items=items,
            summary=summary,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    # ============================================
    # SUCCESS FEE REPORT
    # ============================================

    async def get_success_fee_report(  # noqa: PLR0913, PLR0917
        self,
        company_id: str,
        pagination: PaginationParams,
        client_id: str | None = None,
        carrier_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> SuccessFeeReport:
        """Get success fee report grouped by contract"""
        where = {"companyId": company_id}
        if client_id:
            where["clientId"] = client_id
        if carrier_id:
            where["carrierId"] = carrier_id
        if date_from or date_to:
            where["createdAt"] = {}
            if date_from:
                where["createdAt"]["gte"] = date_from
            if date_to:
                where["createdAt"]["lte"] = date_to

        # Get all contests for grouping
        contests = await self.db.contest.find_many(
            where=where,
            include={"client": True, "carrier": True, "contract": True},
        )

        # Group by contract
        contract_data = defaultdict(
            lambda: {
                "contract_id": None,
                "contract_number": "Sem Contrato",
                "carrier_name": "",
                "client_name": "",
                "success_fee_pct": 0,
                "total_recovered": 0,
                "success_fee_collected": 0,
                "net_to_client": 0,
                "contests_count": 0,
            }
        )

        for c in contests:
            key = c.contractId or "no_contract"
            cd = contract_data[key]
            cd["contract_id"] = c.contractId
            cd["contract_number"] = c.contract.number if c.contract else "Sem Contrato"
            cd["carrier_name"] = c.carrier.name if c.carrier else "N/A"
            cd["client_name"] = c.client.name if c.client else "N/A"
            cd["success_fee_pct"] = c.successFeePct
            cd["total_recovered"] += c.totalRecovered
            cd["success_fee_collected"] += c.successFeeValue
            cd["net_to_client"] += c.netRecovery
            cd["contests_count"] += 1

        items = []
        for v in contract_data.values():
            if v["contests_count"] == 0:
                continue

            # Get contract for progressive pricing info
            pricing_model = "FIXED"
            progressive_month1_pct = None
            progressive_month2_pct = None
            if v["contract_id"]:
                contract = await self.db.contract.find_unique(where={"id": v["contract_id"]})
                if contract:
                    pricing_model = contract.pricingModel
                    if contract.pricingModel == "PROGRESSIVE":
                        progressive_month1_pct = contract.progressiveMonth1Pct
                        progressive_month2_pct = contract.progressiveMonth2Pct

            items.append(
                SuccessFeeReportItem(
                    contract_id=v["contract_id"] or "",
                    contract_number=v["contract_number"],
                    carrier_name=v["carrier_name"],
                    client_name=v["client_name"],
                    success_fee_pct=v["success_fee_pct"],
                    total_recovered=v["total_recovered"],
                    success_fee_collected=v["success_fee_collected"],
                    net_to_client=v["net_to_client"],
                    contests_count=v["contests_count"],
                    pricing_model=pricing_model,
                    progressive_month1_pct=progressive_month1_pct,
                    progressive_month2_pct=progressive_month2_pct,
                )
            )

        # Sort by total_recovered desc
        items.sort(key=lambda x: x.total_recovered, reverse=True)

        total = len(items)
        paginated = items[pagination.offset : pagination.offset + pagination.limit]

        summary = {
            "total_contracts": len(items),
            "total_recovered": sum(i.total_recovered for i in items),
            "total_success_fee": sum(i.success_fee_collected for i in items),
            "total_net_to_client": sum(i.net_to_client for i in items),
            "avg_success_fee_pct": sum(i.success_fee_pct for i in items) / len(items)
            if items
            else 0,
        }

        return SuccessFeeReport(
            items=paginated,
            summary=summary,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

    # ============================================
    # DISCREPANCY STATS
    # ============================================

    async def get_discrepancy_stats(self, company_id: str) -> DiscrepancyStats:
        """Get discrepancy statistics"""
        discrepancies = await self.db.discrepancy.find_many(
            where={"companyId": company_id},
            include={"carrier": True, "client": True},
        )

        by_type = defaultdict(lambda: {"count": 0, "value": 0})
        by_status = defaultdict(int)
        by_carrier = defaultdict(lambda: {"count": 0, "value": 0})
        by_client = defaultdict(lambda: {"count": 0, "value": 0})

        total_detected = 0
        total_approved = 0
        total_recovered = 0
        total_value_detected = 0
        total_value_recovered = 0

        for d in discrepancies:
            by_type[d.type]["count"] += 1
            by_type[d.type]["value"] += d.difference
            by_status[d.status] += 1

            if d.carrierId:
                by_carrier[d.carrierId]["count"] += 1
                by_carrier[d.carrierId]["value"] += d.difference
            if d.clientId:
                by_client[d.clientId]["count"] += 1
                by_client[d.clientId]["value"] += d.difference

            total_value_detected += d.difference
            total_detected += 1
            if d.status == "APPROVED":
                total_approved += 1
            if d.status == "RECOVERED":
                total_recovered += 1
                total_value_recovered += d.difference

        carrier_names = {}
        if by_carrier:
            carriers = await self.db.carrier.find_many(
                where={"id": {"in": list(by_carrier.keys())}}
            )
            carrier_names = {c.id: c.name for c in carriers}

        client_names = {}
        if by_client:
            clients = await self.db.client.find_many(where={"id": {"in": list(by_client.keys())}})
            client_names = {c.id: c.name for c in clients}

        return DiscrepancyStats(
            by_type=[
                {"type": k, "count": v["count"], "value": v["value"]}
                for k, v in sorted(by_type.items(), key=lambda x: x[1]["value"], reverse=True)
            ],
            by_status=[{"status": k, "count": v} for k, v in by_status.items()],
            by_carrier=[
                {
                    "carrier_id": k,
                    "carrier_name": carrier_names.get(k, "N/A"),
                    "count": v["count"],
                    "value": v["value"],
                }
                for k, v in sorted(by_carrier.items(), key=lambda x: x[1]["value"], reverse=True)
            ],
            by_client=[
                {
                    "client_id": k,
                    "client_name": client_names.get(k, "N/A"),
                    "count": v["count"],
                    "value": v["value"],
                }
                for k, v in sorted(by_client.items(), key=lambda x: x[1]["value"], reverse=True)
            ],
            total_detected=total_detected,
            total_approved=total_approved,
            total_recovered=total_recovered,
            total_value_detected=total_value_detected,
            total_value_recovered=total_value_recovered,
        )

    # ============================================
    # EXPORT
    # ============================================

    async def export_report(self, company_id: str, data: ExportRequest) -> ExportResponse:
        """Export report to Excel/CSV/PDF"""
        wb = openpyxl.Workbook()

        if data.report_type == "recovery":
            await self._export_recovery_to_excel(wb, company_id, data)
        elif data.report_type == "success_fee":
            await self._export_success_fee_to_excel(wb, company_id, data)
        elif data.report_type == "discrepancies":
            await self._export_discrepancies_to_excel(wb, company_id, data)
        elif data.report_type == "contests":
            await self._export_contests_to_excel(wb, company_id, data)
        else:
            raise BadRequestError("Invalid report type")

        # Save to bytes
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        excel_bytes = buffer.read()

        # Upload to storage
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{data.report_type}_{timestamp}.xlsx"
        object_name = f"exports/{company_id}/{filename}"

        await upload_file(
            excel_bytes,
            object_name,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Generate presigned URL (valid for 1 hour)
        file_url = await get_presigned_url(object_name, expires=3600)

        return ExportResponse(
            file_url=file_url,
            filename=filename,
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

    async def _export_recovery_to_excel(self, wb, company_id: str, data: ExportRequest):
        """Export recovery report to Excel"""
        ws = wb.active
        ws.title = "Recovery Report"

        # Headers
        headers = [
            "Contest Number",
            "Client",
            "Carrier",
            "Contract",
            "Status",
            "Total Expected",
            "Total Recovered",
            "Success Fee %",
            "Success Fee Value",
            "Net Recovery",
            "Created At",
            "Resolved At",
            "Pricing Model",
            "Progressive Month",
        ]
        self._write_headers(ws, headers)

        # Data
        where = {"companyId": company_id}
        if data.client_id:
            where["clientId"] = data.client_id
        if data.carrier_id:
            where["carrierId"] = data.carrier_id
        if data.date_from or data.date_to:
            where["createdAt"] = {}
            if data.date_from:
                where["createdAt"]["gte"] = data.date_from
            if data.date_to:
                where["createdAt"]["lte"] = data.date_to
        if data.status:
            where["status"] = {"in": data.status}

        contests = await self.db.contest.find_many(
            where=where,
            include={"client": True, "carrier": True, "contract": True},
            order={"createdAt": "desc"},
        )

        for row_idx, c in enumerate(contests, 2):
            # Get pricing model info
            pricing_model = "FIXED"
            progressive_month = None
            if c.contractId:
                contract = await self.db.contract.find_unique(where={"id": c.contractId})
                if contract:
                    pricing_model = contract.pricingModel
                    if contract.pricingModel == "PROGRESSIVE":
                        start_date = contract.progressiveStartDate or contract.startDate
                        check_date = datetime.utcnow()
                        days_diff = (check_date - start_date).days
                        progressive_month = (
                            1
                            if days_diff < PROGRESSIVE_MONTH_DAYS
                            else (days_diff // PROGRESSIVE_MONTH_DAYS) + 1
                        )

            ws.cell(row=row_idx, column=1, value=c.number)
            ws.cell(row=row_idx, column=2, value=c.client.name if c.client else "")
            ws.cell(row=row_idx, column=3, value=c.carrier.name if c.carrier else "")
            ws.cell(row=row_idx, column=4, value=c.contract.number if c.contract else "")
            ws.cell(row=row_idx, column=5, value=c.status)
            ws.cell(row=row_idx, column=6, value=c.totalExpected)
            ws.cell(row=row_idx, column=7, value=c.totalRecovered)
            ws.cell(row=row_idx, column=8, value=c.successFeePct)
            ws.cell(row=row_idx, column=9, value=c.successFeeValue)
            ws.cell(row=row_idx, column=10, value=c.netRecovery)
            ws.cell(
                row=row_idx,
                column=11,
                value=c.createdAt.strftime("%d/%m/%Y") if c.createdAt else "",
            )
            ws.cell(
                row=row_idx,
                column=12,
                value=c.resolvedAt.strftime("%d/%m/%Y") if c.resolvedAt else "",
            )
            ws.cell(row=row_idx, column=13, value=pricing_model)
            ws.cell(row=row_idx, column=14, value=progressive_month)

        self._format_currency_columns(ws, [6, 7, 9, 10])
        self._auto_width(ws)

    async def _export_success_fee_to_excel(self, wb, company_id: str, data: ExportRequest):  # noqa: PLR0915
        """Export success fee report to Excel"""
        ws = wb.active
        ws.title = "Success Fee Report"

        headers = [
            "Contract Number",
            "Client",
            "Carrier",
            "Success Fee %",
            "Total Recovered",
            "Success Fee Collected",
            "Net to Client",
            "Contests Count",
            "Pricing Model",
            "Month 1 %",
            "Month 2+ %",
        ]
        self._write_headers(ws, headers)

        where = {"companyId": company_id}
        if data.client_id:
            where["clientId"] = data.client_id
        if data.carrier_id:
            where["carrierId"] = data.carrier_id
        if data.date_from or data.date_to:
            where["createdAt"] = {}
            if data.date_from:
                where["createdAt"]["gte"] = data.date_from
            if data.date_to:
                where["createdAt"]["lte"] = data.date_to

        contests = await self.db.contest.find_many(
            where=where,
            include={"client": True, "carrier": True, "contract": True},
        )

        # Group by contract
        contract_data = defaultdict(
            lambda: {
                "contract_number": "Sem Contrato",
                "carrier_name": "",
                "client_name": "",
                "success_fee_pct": 0,
                "total_recovered": 0,
                "success_fee_collected": 0,
                "net_to_client": 0,
                "contests_count": 0,
            }
        )

        for c in contests:
            key = c.contractId or "no_contract"
            cd = contract_data[key]
            cd["contract_number"] = c.contract.number if c.contract else "Sem Contrato"
            cd["carrier_name"] = c.carrier.name if c.carrier else "N/A"
            cd["client_name"] = c.client.name if c.client else "N/A"
            cd["success_fee_pct"] = c.successFeePct
            cd["total_recovered"] += c.totalRecovered
            cd["success_fee_collected"] += c.successFeeValue
            cd["net_to_client"] += c.netRecovery
            cd["contests_count"] += 1

        for row_idx, v in enumerate(contract_data.values(), 2):
            if v["contests_count"] == 0:
                continue

            # Get contract for progressive pricing info
            pricing_model = "FIXED"
            month1_pct = None
            month2_pct = None
            if v.get("contract_id"):
                contract = await self.db.contract.find_unique(where={"id": v["contract_id"]})
                if contract:
                    pricing_model = contract.pricingModel
                    if contract.pricingModel == "PROGRESSIVE":
                        month1_pct = contract.progressiveMonth1Pct
                        month2_pct = contract.progressiveMonth2Pct

            ws.cell(row=row_idx, column=1, value=v["contract_number"])
            ws.cell(row=row_idx, column=2, value=v["client_name"])
            ws.cell(row=row_idx, column=3, value=v["carrier_name"])
            ws.cell(row=row_idx, column=4, value=v["success_fee_pct"])
            ws.cell(row=row_idx, column=5, value=v["total_recovered"])
            ws.cell(row=row_idx, column=6, value=v["success_fee_collected"])
            ws.cell(row=row_idx, column=7, value=v["net_to_client"])
            ws.cell(row=row_idx, column=8, value=v["contests_count"])
            ws.cell(row=row_idx, column=9, value=pricing_model)
            ws.cell(row=row_idx, column=10, value=month1_pct)
            ws.cell(row=row_idx, column=11, value=month2_pct)

        self._format_currency_columns(ws, [5, 6, 7])
        self._auto_width(ws)

    async def _export_discrepancies_to_excel(self, wb, company_id: str, data: ExportRequest):
        """Export discrepancies to Excel"""
        ws = wb.active
        ws.title = "Discrepancies"

        headers = [
            "ID",
            "Type",
            "Status",
            "Rule Code",
            "Rule Description",
            "Expected",
            "Actual",
            "Difference",
            "Difference %",
            "Carrier",
            "Client",
            "Branch",
            "Document",
            "Created At",
        ]
        self._write_headers(ws, headers)

        where = {"companyId": company_id}
        if data.date_from or data.date_to:
            where["createdAt"] = {}
            if data.date_from:
                where["createdAt"]["gte"] = data.date_from
            if data.date_to:
                where["createdAt"]["lte"] = data.date_to
        if data.status:
            where["status"] = {"in": data.status}

        discrepancies = await self.db.discrepancy.find_many(
            where=where,
            include={"carrier": True, "client": True, "branch": True, "document": True},
            order={"createdAt": "desc"},
        )

        for row_idx, d in enumerate(discrepancies, 2):
            ws.cell(row=row_idx, column=1, value=d.id)
            ws.cell(row=row_idx, column=2, value=d.type)
            ws.cell(row=row_idx, column=3, value=d.status)
            ws.cell(row=row_idx, column=4, value=d.ruleCode)
            ws.cell(row=row_idx, column=5, value=d.ruleDescription)
            ws.cell(row=row_idx, column=6, value=d.expectedValue)
            ws.cell(row=row_idx, column=7, value=d.actualValue)
            ws.cell(row=row_idx, column=8, value=d.difference)
            ws.cell(row=row_idx, column=9, value=d.differencePct)
            ws.cell(row=row_idx, column=10, value=d.carrier.name if d.carrier else "")
            ws.cell(row=row_idx, column=11, value=d.client.name if d.client else "")
            ws.cell(row=row_idx, column=12, value=d.branch.name if d.branch else "")
            ws.cell(row=row_idx, column=13, value=d.document.originalName if d.document else "")
            ws.cell(
                row=row_idx,
                column=14,
                value=d.createdAt.strftime("%d/%m/%Y") if d.createdAt else "",
            )

        self._format_currency_columns(ws, [6, 7, 8])
        self._auto_width(ws)

    async def _export_contests_to_excel(self, wb, company_id: str, data: ExportRequest):
        """Export contests to Excel"""
        ws = wb.active
        ws.title = "Contests"

        headers = [
            "Number",
            "Status",
            "Client",
            "Carrier",
            "Contract",
            "Total Expected",
            "Total Recovered",
            "Success Fee %",
            "Success Fee Value",
            "Net Recovery",
            "Sent At",
            "Resolved At",
        ]
        self._write_headers(ws, headers)

        where = {"companyId": company_id}
        if data.client_id:
            where["clientId"] = data.client_id
        if data.carrier_id:
            where["carrierId"] = data.carrier_id
        if data.date_from or data.date_to:
            where["createdAt"] = {}
            if data.date_from:
                where["createdAt"]["gte"] = data.date_from
            if data.date_to:
                where["createdAt"]["lte"] = data.date_to
        if data.status:
            where["status"] = {"in": data.status}

        contests = await self.db.contest.find_many(
            where=where,
            include={"client": True, "carrier": True, "contract": True},
            order={"createdAt": "desc"},
        )

        for row_idx, c in enumerate(contests, 2):
            ws.cell(row=row_idx, column=1, value=c.number)
            ws.cell(row=row_idx, column=2, value=c.status)
            ws.cell(row=row_idx, column=3, value=c.client.name if c.client else "")
            ws.cell(row=row_idx, column=4, value=c.carrier.name if c.carrier else "")
            ws.cell(row=row_idx, column=5, value=c.contract.number if c.contract else "")
            ws.cell(row=row_idx, column=6, value=c.totalExpected)
            ws.cell(row=row_idx, column=7, value=c.totalRecovered)
            ws.cell(row=row_idx, column=8, value=c.successFeePct)
            ws.cell(row=row_idx, column=9, value=c.successFeeValue)
            ws.cell(row=row_idx, column=10, value=c.netRecovery)
            ws.cell(row=row_idx, column=11, value=c.sentAt.strftime("%d/%m/%Y") if c.sentAt else "")
            ws.cell(
                row=row_idx,
                column=12,
                value=c.resolvedAt.strftime("%d/%m/%Y") if c.resolvedAt else "",
            )

        self._format_currency_columns(ws, [6, 7, 9, 10])
        self._auto_width(ws)

    def _write_headers(self, ws, headers: list[str]):
        """Write header row with styling"""
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1e3a5f", end_color="1e3a5f", fill_type="solid")
        header_alignment = Alignment(horizontal="center", wrap_text=True)
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

    def _format_currency_columns(self, ws, cols: list[int]):
        """Format columns as currency"""
        for row in ws.iter_rows(
            min_row=2, max_row=ws.max_row, min_col=min(cols), max_col=max(cols)
        ):
            for cell in row:
                if cell.column in cols and cell.value is not None:
                    cell.number_format = "R$ #,##0.00"

    def _auto_width(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
