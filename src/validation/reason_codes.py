"""Reason-code validation for remittance stubs.

Checks that every deduction reason code maps to a known category
in the retailer's YAML config. Also provides full stub validation
combining arithmetic and reason-code checks.
"""

from src.models import (
    RemittanceStub,
    ValidationDetail,
    ValidationResult,
    ValidationStatus,
    load_reason_codes,
)
from src.validation.arithmetic import validate_arithmetic


def validate_reason_codes(
    stub: RemittanceStub,
) -> tuple[bool, list[ValidationDetail]]:
    """Check that all deduction reason codes map to known categories.

    Returns (all_mapped, details) where details lists any unmapped codes.
    """
    try:
        known_codes = load_reason_codes(stub.retailer)
    except FileNotFoundError:
        # No config at all — every code is unmapped
        details = [
            ValidationDetail(
                field="reason_code",
                issue=f"No reason-code config found for retailer {stub.retailer.value}",
            )
        ]
        return False, details

    unmapped_details: list[ValidationDetail] = []

    for deduction in stub.deductions:
        if deduction.reason_code not in known_codes:
            unmapped_details.append(
                ValidationDetail(
                    field="reason_code",
                    issue=f"Unmapped reason code '{deduction.reason_code}' "
                    f"on invoice {deduction.invoice_number}",
                    expected="A code from the retailer config",
                    actual=deduction.reason_code,
                )
            )

    all_mapped = len(unmapped_details) == 0
    return all_mapped, unmapped_details


def validate_stub(stub: RemittanceStub, stub_id: str = "") -> ValidationResult:
    """Full validation: arithmetic + reason codes.

    Status is VERIFIED only if arithmetic balances AND all codes are mapped.
    """
    # Run arithmetic check first
    arithmetic_result = validate_arithmetic(stub, stub_id=stub_id)

    # Run reason-code check
    all_codes_mapped, code_details = validate_reason_codes(stub)

    # Combine results
    is_verified = arithmetic_result.arithmetic_valid and all_codes_mapped
    combined_details = list(arithmetic_result.details) + code_details

    return ValidationResult(
        stub_id=arithmetic_result.stub_id,
        status=ValidationStatus.VERIFIED if is_verified else ValidationStatus.FLAGGED,
        arithmetic_valid=arithmetic_result.arithmetic_valid,
        all_codes_mapped=all_codes_mapped,
        discrepancy_amount=arithmetic_result.discrepancy_amount,
        details=combined_details,
    )
