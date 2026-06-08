"""Tests for the validation layer (arithmetic + reason-code checks)."""

from datetime import date
from decimal import Decimal

import pytest

from src.models import (
    DeductionEntry,
    RemittanceStub,
    RetailerFormat,
    ValidationStatus,
)
from src.validation.arithmetic import validate_arithmetic
from src.validation.reason_codes import validate_reason_codes, validate_stub


# --- helpers ---

def _make_stub(
    gross: str = "10000.00",
    net: str = "8000.00",
    deductions: list[tuple[str, str, str]] | None = None,
    retailer: RetailerFormat = RetailerFormat.WALMART,
) -> RemittanceStub:
    """Build a stub for testing.

    deductions: list of (invoice_number, reason_code, amount) tuples.
    If None, defaults to two Walmart deductions that sum to gross - net.
    """
    if deductions is None:
        diff = Decimal(gross) - Decimal(net)
        half = (diff / 2).quantize(Decimal("0.01"))
        remainder = diff - half
        deductions = [
            ("WM-100001", "22", str(half)),
            ("WM-100002", "41", str(remainder)),
        ]

    entries = [
        DeductionEntry(
            invoice_number=inv,
            reason_code=code,
            reason_description="test",
            amount=Decimal(amt),
            deduction_date=date(2025, 6, 1),
        )
        for inv, code, amt in deductions
    ]

    return RemittanceStub(
        retailer=retailer,
        check_number="CHK-TEST-001",
        payment_date=date(2025, 7, 1),
        gross_invoice=Decimal(gross),
        net_cash=Decimal(net),
        payer_name="Test Payer",
        deductions=entries,
    )


# --- arithmetic validation ---

class TestArithmeticValidation:
    def test_verified_when_stub_balances(self):
        """Clean stub where net + deductions = gross exactly."""
        stub = _make_stub(gross="10000.00", net="8000.00")
        result = validate_arithmetic(stub, stub_id="test-1")

        assert result.status == ValidationStatus.VERIFIED
        assert result.arithmetic_valid is True
        assert result.discrepancy_amount is None
        assert result.details == []

    def test_flagged_when_gross_too_high(self):
        """Gross is $42.50 higher than net + deductions."""
        stub = _make_stub(
            gross="10042.50",
            net="8000.00",
            deductions=[
                ("WM-100001", "22", "1000.00"),
                ("WM-100002", "41", "1000.00"),
            ],
        )
        result = validate_arithmetic(stub, stub_id="test-2")

        assert result.status == ValidationStatus.FLAGGED
        assert result.arithmetic_valid is False
        assert result.discrepancy_amount == Decimal("42.50")
        assert len(result.details) == 1
        assert "mismatch" in result.details[0].issue.lower()

    def test_flagged_when_gross_too_low(self):
        """Gross is lower than net + deductions."""
        stub = _make_stub(
            gross="9900.00",
            net="8000.00",
            deductions=[
                ("WM-100001", "22", "1000.00"),
                ("WM-100002", "41", "1000.00"),
            ],
        )
        result = validate_arithmetic(stub, stub_id="test-3")

        assert result.status == ValidationStatus.FLAGGED
        assert result.arithmetic_valid is False
        assert result.discrepancy_amount == Decimal("100.00")

    def test_uses_check_number_when_no_stub_id(self):
        """Default stub_id falls back to check_number."""
        stub = _make_stub()
        result = validate_arithmetic(stub)
        assert result.stub_id == "CHK-TEST-001"

    def test_verified_with_no_deductions(self):
        """Stub with zero deductions: net should equal gross."""
        stub = _make_stub(
            gross="5000.00",
            net="5000.00",
            deductions=[],
        )
        result = validate_arithmetic(stub, stub_id="test-4")
        assert result.status == ValidationStatus.VERIFIED

    def test_discrepancy_amount_is_absolute(self):
        """Discrepancy is always positive regardless of direction."""
        stub = _make_stub(
            gross="9000.00",  # 1000 less than net + deductions
            net="8000.00",
            deductions=[("WM-100001", "22", "2000.00")],
        )
        result = validate_arithmetic(stub, stub_id="test-5")
        assert result.discrepancy_amount == Decimal("1000.00")


# --- reason-code validation ---

class TestReasonCodeValidation:
    def test_all_mapped_when_codes_are_known(self):
        """All Walmart codes are in the config."""
        stub = _make_stub(
            deductions=[
                ("WM-100001", "22", "500.00"),
                ("WM-100002", "41", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is True
        assert details == []

    def test_not_mapped_when_code_unknown(self):
        """Code 'ZZ' is not in Walmart's config."""
        stub = _make_stub(
            deductions=[
                ("WM-100001", "22", "500.00"),
                ("WM-100002", "ZZ", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is False
        assert len(details) == 1
        assert "ZZ" in details[0].issue

    def test_multiple_unmapped_codes(self):
        """Two unknown codes produce two details."""
        stub = _make_stub(
            deductions=[
                ("WM-100001", "ZZ", "500.00"),
                ("WM-100002", "YY", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is False
        assert len(details) == 2

    def test_costco_codes_validated_correctly(self):
        """Costco codes use letter-based codes."""
        stub = _make_stub(
            retailer=RetailerFormat.COSTCO,
            deductions=[
                ("CS-100001", "AD", "500.00"),
                ("CS-100002", "SH", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is True

    def test_unfi_codes_validated_correctly(self):
        """UNFI uses three-letter codes."""
        stub = _make_stub(
            retailer=RetailerFormat.UNFI,
            deductions=[
                ("UNF-100001", "MCB", "500.00"),
                ("UNF-100002", "OSD", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is True

    def test_kehe_codes_validated_correctly(self):
        """KeHE uses three-letter codes."""
        stub = _make_stub(
            retailer=RetailerFormat.KEHE,
            deductions=[
                ("KH-100001", "MKD", "500.00"),
                ("KH-100002", "DMG", "500.00"),
            ],
        )
        all_mapped, details = validate_reason_codes(stub)
        assert all_mapped is True


# --- full stub validation ---

class TestFullValidation:
    def test_verified_when_arithmetic_and_codes_pass(self):
        """Clean stub with all mapped codes is VERIFIED."""
        stub = _make_stub()
        result = validate_stub(stub, stub_id="full-1")

        assert result.status == ValidationStatus.VERIFIED
        assert result.arithmetic_valid is True
        assert result.all_codes_mapped is True
        assert result.details == []

    def test_flagged_when_arithmetic_fails_but_codes_pass(self):
        """Broken arithmetic with mapped codes is FLAGGED."""
        stub = _make_stub(
            gross="10042.50",
            net="8000.00",
            deductions=[
                ("WM-100001", "22", "1000.00"),
                ("WM-100002", "41", "1000.00"),
            ],
        )
        result = validate_stub(stub, stub_id="full-2")

        assert result.status == ValidationStatus.FLAGGED
        assert result.arithmetic_valid is False
        assert result.all_codes_mapped is True
        assert result.discrepancy_amount == Decimal("42.50")

    def test_flagged_when_codes_unmapped_but_arithmetic_passes(self):
        """Clean arithmetic with unmapped code is FLAGGED."""
        stub = _make_stub(
            gross="10000.00",
            net="8000.00",
            deductions=[
                ("WM-100001", "22", "1000.00"),
                ("WM-100002", "ZZ", "1000.00"),
            ],
        )
        result = validate_stub(stub, stub_id="full-3")

        assert result.status == ValidationStatus.FLAGGED
        assert result.arithmetic_valid is True
        assert result.all_codes_mapped is False
        assert len(result.details) == 1  # one unmapped code detail

    def test_flagged_when_both_fail(self):
        """Broken arithmetic AND unmapped code is FLAGGED with all details."""
        stub = _make_stub(
            gross="10050.00",
            net="8000.00",
            deductions=[
                ("WM-100001", "22", "1000.00"),
                ("WM-100002", "ZZ", "1000.00"),
            ],
        )
        result = validate_stub(stub, stub_id="full-4")

        assert result.status == ValidationStatus.FLAGGED
        assert result.arithmetic_valid is False
        assert result.all_codes_mapped is False
        # One arithmetic detail + one unmapped code detail
        assert len(result.details) == 2
