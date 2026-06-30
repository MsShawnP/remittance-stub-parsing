"""Reconciliation against Cinderhaven SSOT data.

Matches deduction invoice numbers against reference invoice records
to determine how much of a stub's deductions can be verified against
the accounts-receivable ledger. Also calculates dispute window
exposure — days remaining before unreconciled deductions expire
past the standard 90-day dispute window.
"""

from datetime import date
from decimal import Decimal

from src.models import ReconciliationMatch, ReconciliationResult, RemittanceStub

# Cinderhaven canonical figures
ANNUAL_TRADE_SPEND = Decimal("3600000")  # ~$3.6M/yr
TOTAL_CHARGEBACKS = 3357
DISPUTE_WINDOW_DAYS = 90  # standard dispute window


def reconcile_stub(
    stub: RemittanceStub,
    reference_invoices: dict,
    stub_id: str = "",
    as_of_date: date | None = None,
) -> ReconciliationResult:
    """Reconcile a stub's deductions against Cinderhaven reference invoice data.

    Args:
        stub: The remittance stub to reconcile.
        reference_invoices: Dict mapping invoice_number -> {"amount": Decimal, "date": date}.
        stub_id: Identifier for this stub. Defaults to check_number.
        as_of_date: Date to calculate dispute window from. Defaults to today.

    Returns:
        ReconciliationResult with match status, matched/unmatched amounts,
        and days remaining in the dispute window.
    """
    effective_id = stub_id or stub.check_number
    today = as_of_date or date.today()

    matched_amount = Decimal("0")
    unmatched_amount = Decimal("0")
    details: list[str] = []
    min_days_remaining: int | None = None

    for deduction in stub.deductions:
        invoice_key = deduction.invoice_number

        if invoice_key in reference_invoices:
            ref = reference_invoices[invoice_key]
            ref_amount = Decimal(str(ref["amount"]))

            if ref_amount == deduction.amount:
                matched_amount += deduction.amount
                details.append(
                    f"MATCHED: {invoice_key} — ${deduction.amount} "
                    f"matches reference exactly"
                )
            else:
                # Partial match — amounts differ
                matched_amount += min(deduction.amount, ref_amount)
                diff = abs(deduction.amount - ref_amount)
                unmatched_amount += diff
                details.append(
                    f"PARTIAL: {invoice_key} — deduction ${deduction.amount} "
                    f"vs reference ${ref_amount} (diff ${diff})"
                )
        else:
            unmatched_amount += deduction.amount
            details.append(
                f"UNMATCHED: {invoice_key} — ${deduction.amount} "
                f"has no reference invoice"
            )

        # Calculate dispute window from deduction date
        deduction_date = deduction.deduction_date or stub.payment_date
        if deduction_date:
            days_elapsed = (today - deduction_date).days
            days_remaining = max(0, DISPUTE_WINDOW_DAYS - days_elapsed)
            if min_days_remaining is None or days_remaining < min_days_remaining:
                min_days_remaining = days_remaining

    # Determine overall match status
    if unmatched_amount == Decimal("0") and matched_amount > Decimal("0"):
        match_status = ReconciliationMatch.MATCHED
    elif matched_amount > Decimal("0") and unmatched_amount > Decimal("0"):
        match_status = ReconciliationMatch.PARTIAL
    else:
        match_status = ReconciliationMatch.UNMATCHED

    return ReconciliationResult(
        stub_id=effective_id,
        match_status=match_status,
        matched_amount=matched_amount,
        unmatched_amount=unmatched_amount,
        dispute_window_days_remaining=min_days_remaining,
        details=details,
    )
