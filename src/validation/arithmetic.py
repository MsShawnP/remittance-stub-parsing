"""Arithmetic validation for remittance stubs.

Verifies that net_cash + sum(deduction_amounts) == gross_invoice.
Uses Decimal arithmetic throughout to avoid floating-point drift.
"""

from decimal import Decimal

from src.models import (
    RemittanceStub,
    ValidationDetail,
    ValidationResult,
    ValidationStatus,
)


def validate_arithmetic(stub: RemittanceStub, stub_id: str = "") -> ValidationResult:
    """Check that net_cash + sum(deduction_amounts) == gross_invoice.

    Returns ValidationResult with status VERIFIED if it balances to the penny,
    FLAGGED with discrepancy details if it doesn't.

    Args:
        stub: The remittance stub to validate.
        stub_id: Identifier for this stub in the result. Defaults to
                 the stub's check_number if empty.
    """
    effective_id = stub_id or stub.check_number

    total_deductions = sum(
        (d.amount for d in stub.deductions), start=Decimal("0")
    )
    expected_gross = stub.net_cash + total_deductions
    discrepancy = stub.gross_invoice - expected_gross

    if discrepancy == Decimal("0"):
        return ValidationResult(
            stub_id=effective_id,
            status=ValidationStatus.VERIFIED,
            arithmetic_valid=True,
            all_codes_mapped=True,  # placeholder — reason_codes sets the real value
        )

    return ValidationResult(
        stub_id=effective_id,
        status=ValidationStatus.FLAGGED,
        arithmetic_valid=False,
        all_codes_mapped=True,  # placeholder
        discrepancy_amount=abs(discrepancy),
        details=[
            ValidationDetail(
                field="gross_invoice",
                issue="Arithmetic mismatch: net_cash + sum(deductions) != gross_invoice",
                expected=str(expected_gross),
                actual=str(stub.gross_invoice),
            )
        ],
    )
