"""Tests for PDF Generator service"""

import asyncio

import pytest

from app.services.pdf_generator import generate_contest_letter

# Test constants
CONCURRENT_TASKS = 5


class TestPDFGenerator:
    """Tests for PDF generation"""

    @pytest.fixture
    def sample_contest(self):
        """Sample contest data for testing"""
        return {
            "number": "CTST-2024-001",
            "status": "DRAFT",
            "items": [
                {
                    "discrepancy": {"type": "ICMS_DIFFERENTIAL", "ruleCode": "ICMS_DIFAL"},
                    "expected_value": 1000.0,
                    "actual_value": 1100.0,
                    "contested_value": 1100.0,
                    "difference": 100.0,
                    "difference_pct": 10.0,
                },
                {
                    "discrepancy": {"type": "FREIGHT_WEIGHT_VALUE", "ruleCode": "FRETE_PESO_VALOR"},
                    "expected_value": 500.0,
                    "actual_value": 550.0,
                    "contested_value": 550.0,
                    "difference": 50.0,
                    "difference_pct": 10.0,
                },
            ],
            "success_fee_pct": 25.0,
            "success_fee_value": 387.5,
            "net_recovery": 1162.5,
        }

    @pytest.fixture
    def sample_client(self):
        """Sample client data"""
        return {
            "name": "Empresa Teste Ltda",
            "cnpj": "12345678000195",
        }

    @pytest.fixture
    def sample_carrier(self):
        """Sample carrier data"""
        return {
            "name": "Transportadora Exemplo S.A.",
            "cnpj": "98765432000123",
        }

    @pytest.fixture
    def sample_company(self):
        """Sample company data"""
        return {
            "name": "AVERTA S.A.",
            "email": "contato@averta.com",
            "website": "www.averta.com",
        }

    @pytest.mark.asyncio
    async def test_generate_small_pdf_sync(
        self, sample_contest, sample_client, sample_carrier, sample_company
    ):
        """Test generating a small PDF completes quickly and returns valid PDF bytes"""
        pdf_bytes = await generate_contest_letter(
            contest=sample_contest,
            client=sample_client,
            carrier=sample_carrier,
            company=sample_company,
            timeout=5.0,  # Short timeout for small PDF
        )

        # Verify we got PDF bytes
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

        # Verify PDF magic number (%PDF)
        assert pdf_bytes.startswith(b"%PDF")

        # Verify it's a complete PDF
        assert b"%%EOF" in pdf_bytes[-100:]

    @pytest.mark.asyncio
    async def test_generate_pdf_with_many_items(
        self, sample_client, sample_carrier, sample_company
    ):
        """Test generating PDF with many discrepancy items (larger PDF)"""
        # Create contest with many items to simulate a larger PDF
        large_contest = {
            "number": "CTST-2024-099",
            "status": "SENT",
            "items": [
                {
                    "discrepancy": {"type": "ICMS_DIFFERENTIAL", "ruleCode": "ICMS_DIFAL"},
                    "expected_value": 1000.0 + i * 10,
                    "actual_value": 1100.0 + i * 10,
                    "contested_value": 1100.0 + i * 10,
                    "difference": 100.0 + i * 10,
                    "difference_pct": 10.0,
                }
                for i in range(50)  # 50 items = larger table
            ],
            "success_fee_pct": 25.0,
            "success_fee_value": 5000.0,
            "net_recovery": 15000.0,
        }

        pdf_bytes = await generate_contest_letter(
            contest=large_contest,
            client=sample_client,
            carrier=sample_carrier,
            company=sample_company,
            timeout=10.0,  # Slightly longer timeout for larger PDF
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")
        assert b"%%EOF" in pdf_bytes[-100:]

    @pytest.mark.asyncio
    async def test_generate_pdf_timeout_enforcement(
        self, sample_client, sample_carrier, sample_company
    ):
        """Test that timeout is enforced for slow PDF generation"""
        # Create a contest that would take a long time
        # We use a very short timeout to force a timeout
        slow_contest = {
            "number": "CTST-2024-SLOW",
            "status": "DRAFT",
            "items": [
                {
                    "discrepancy": {"type": "ICMS_DIFFERENTIAL", "ruleCode": "ICMS_DIFAL"},
                    "expected_value": 1000.0,
                    "actual_value": 1100.0,
                    "contested_value": 1100.0,
                    "difference": 100.0,
                    "difference_pct": 10.0,
                }
            ],
            "success_fee_pct": 25.0,
            "success_fee_value": 250.0,
            "net_recovery": 750.0,
        }

        # Test with extremely short timeout - should raise TimeoutError
        with pytest.raises(asyncio.TimeoutError):
            await generate_contest_letter(
                contest=slow_contest,
                client=sample_client,
                carrier=sample_carrier,
                company=sample_company,
                timeout=0.001,  # 1ms - should always timeout
            )

    @pytest.mark.asyncio
    async def test_generate_pdf_with_custom_template(
        self, sample_contest, sample_client, sample_carrier, sample_company
    ):
        """Test generating PDF with custom template parameter"""
        pdf_bytes = await generate_contest_letter(
            contest=sample_contest,
            client=sample_client,
            carrier=sample_carrier,
            company=sample_company,
            template="custom_template",
            timeout=5.0,
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_generate_pdf_uses_default_timeout(
        self, sample_contest, sample_client, sample_carrier, sample_company
    ):
        """Test that default timeout is used when not specified"""
        # This test verifies the function works without explicit timeout
        # (using the module-level PDF_GENERATION_TIMEOUT)
        pdf_bytes = await generate_contest_letter(
            contest=sample_contest,
            client=sample_client,
            carrier=sample_carrier,
            company=sample_company,
            # No timeout specified - should use default
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_pdf_structure_valid(
        self, sample_contest, sample_client, sample_carrier, sample_company
    ):
        """Test that generated PDF has valid structure"""
        pdf_bytes = await generate_contest_letter(
            contest=sample_contest,
            client=sample_client,
            carrier=sample_carrier,
            company=sample_company,
            timeout=5.0,
        )

        # Verify PDF structure - basic checks
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")
        assert b"%%EOF" in pdf_bytes[-100:]

        # Verify it has basic PDF objects
        assert b"obj" in pdf_bytes
        assert b"endobj" in pdf_bytes
        assert b"stream" in pdf_bytes
        assert b"endstream" in pdf_bytes

    @pytest.mark.asyncio
    async def test_concurrent_pdf_generation(
        self, sample_contest, sample_client, sample_carrier, sample_company
    ):
        """Test multiple PDF generations can run concurrently"""
        # Generate multiple PDFs concurrently
        tasks = [
            generate_contest_letter(
                contest={**sample_contest, "number": f"CTST-2024-{i:03d}"},
                client=sample_client,
                carrier=sample_carrier,
                company=sample_company,
                timeout=5.0,
            )
            for i in range(CONCURRENT_TASKS)
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == CONCURRENT_TASKS
        for pdf_bytes in results:
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0
            assert pdf_bytes.startswith(b"%PDF")


class TestPDFGeneratorEdgeCases:
    """Edge case tests for PDF generator"""

    @pytest.fixture
    def minimal_data(self):
        """Minimal data for edge case testing"""
        return {
            "contest": {
                "number": "MIN-001",
                "status": "DRAFT",
                "items": [],
                "success_fee_pct": 0.0,
                "success_fee_value": 0.0,
                "net_recovery": 0.0,
            },
            "client": {"name": "Min Client", "cnpj": ""},
            "carrier": {"name": "Min Carrier", "cnpj": ""},
            "company": {"name": "Min Company", "email": "", "website": ""},
        }

    @pytest.mark.asyncio
    async def test_generate_pdf_with_empty_items(self, minimal_data):
        """Test generating PDF with no discrepancy items"""
        pdf_bytes = await generate_contest_letter(
            contest=minimal_data["contest"],
            client=minimal_data["client"],
            carrier=minimal_data["carrier"],
            company=minimal_data["company"],
            timeout=5.0,
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    @pytest.mark.asyncio
    async def test_generate_pdf_with_special_characters(self, minimal_data):
        """Test generating PDF with special characters in names"""
        minimal_data["client"]["name"] = "Empresa & Cia Ltda – São Paulo"
        minimal_data["carrier"]["name"] = "Transportação Ltda (São Paulo)"
        minimal_data["company"]["name"] = "AVERTA – Auditoria & Consultoria"

        pdf_bytes = await generate_contest_letter(
            contest=minimal_data["contest"],
            client=minimal_data["client"],
            carrier=minimal_data["carrier"],
            company=minimal_data["company"],
            timeout=5.0,
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
