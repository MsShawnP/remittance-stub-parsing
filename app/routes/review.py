"""Review queue routes: flagged stub listing, detail view, revalidation."""

import asyncio
import threading
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.extraction.pipeline import extract
from src.models import DeductionEntry, RemittanceStub, ValidationStatus
from src.validation.reason_codes import validate_stub

router = APIRouter(prefix="/review")

STUBS_DIR = Path(__file__).parent.parent.parent / "stubs"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# In-memory store of processed results, keyed by filename.
# Populated when stubs are processed via /process or /tour.
_processed_stubs: dict[str, dict] = {}
_processed_lock = threading.Lock()


def _safe_stub_path(filename: str) -> Path:
    """Resolve a stub filename and verify it stays within STUBS_DIR."""
    pdf_path = (STUBS_DIR / filename).resolve()
    if not pdf_path.is_relative_to(STUBS_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not pdf_path.exists() or pdf_path.suffix != ".pdf":
        raise HTTPException(status_code=404, detail=f"Stub not found: {filename}")
    return pdf_path


def _ensure_processed(filename: str) -> dict:
    """Process a stub if it hasn't been processed yet, return cached result."""
    with _processed_lock:
        if filename not in _processed_stubs:
            pdf_path = _safe_stub_path(filename)

            extraction_result = extract(pdf_path, skip_llm=True)
            validation = validate_stub(extraction_result.stub, stub_id=filename)
            _processed_stubs[filename] = {
                "stub": extraction_result.stub,
                "validation": validation,
                "extraction_method": extraction_result.method,
                "filename": filename,
            }
        return _processed_stubs[filename]


def _get_flagged_stubs() -> list[dict]:
    """Process all stubs and return those with FLAGGED status."""
    flagged = []
    if not STUBS_DIR.exists():
        return flagged

    for pdf in sorted(STUBS_DIR.glob("*.pdf")):
        result = _ensure_processed(pdf.name)
        if result["validation"].status == ValidationStatus.FLAGGED:
            flagged.append(result)
    return flagged


@router.get("", response_class=HTMLResponse)
async def review_queue(request: Request):
    """Review queue page listing all flagged stubs."""
    flagged = _get_flagged_stubs()
    return templates.TemplateResponse(
        request,
        "review.html",
        context={"flagged_stubs": flagged},
    )


@router.get("/{stub_filename}", response_class=HTMLResponse)
async def review_detail(stub_filename: str, request: Request):
    """Review detail page with side-by-side PDF viewer and editable form."""
    _safe_stub_path(stub_filename)
    result = _ensure_processed(stub_filename)

    return templates.TemplateResponse(
        request,
        "review.html",
        context={
            "flagged_stubs": _get_flagged_stubs(),
            "active_stub": result,
        },
    )


@router.post("/{stub_filename}/revalidate", response_class=HTMLResponse)
async def revalidate_stub(stub_filename: str, request: Request):
    """Accept edited form data, rebuild the stub, revalidate, return updated partial.

    Form fields:
    - gross_invoice: Decimal string
    - net_cash: Decimal string
    - deduction_{i}_invoice: invoice number for row i
    - deduction_{i}_reason_code: reason code for row i
    - deduction_{i}_description: description for row i
    - deduction_{i}_amount: Decimal string for row i
    """
    _safe_stub_path(stub_filename)

    # Get the original stub for fields we don't edit
    original = _ensure_processed(stub_filename)
    original_stub = original["stub"]

    form_data = await request.form()

    # Parse totals
    try:
        gross_invoice = Decimal(str(form_data.get("gross_invoice", "0")).replace(",", ""))
    except (InvalidOperation, ValueError):
        gross_invoice = original_stub.gross_invoice

    try:
        net_cash = Decimal(str(form_data.get("net_cash", "0")).replace(",", ""))
    except (InvalidOperation, ValueError):
        net_cash = original_stub.net_cash

    # Parse deduction rows from form (capped to prevent abuse)
    max_deductions = 200
    deductions = []
    i = 0
    while f"deduction_{i}_invoice" in form_data and i < max_deductions:
        invoice_number = str(form_data.get(f"deduction_{i}_invoice", ""))
        reason_code = str(form_data.get(f"deduction_{i}_reason_code", ""))
        description = str(form_data.get(f"deduction_{i}_description", ""))
        amount_str = str(form_data.get(f"deduction_{i}_amount", "0")).replace(",", "")

        try:
            amount = Decimal(amount_str)
        except (InvalidOperation, ValueError):
            amount = Decimal("0")

        deductions.append(
            DeductionEntry(
                invoice_number=invoice_number,
                reason_code=reason_code,
                reason_description=description,
                amount=amount,
            )
        )
        i += 1

    # Build updated stub
    updated_stub = RemittanceStub(
        retailer=original_stub.retailer,
        check_number=original_stub.check_number,
        payment_date=original_stub.payment_date,
        gross_invoice=gross_invoice,
        net_cash=net_cash,
        payer_name=original_stub.payer_name,
        deductions=deductions,
        source_file=original_stub.source_file,
    )

    # Revalidate
    validation = validate_stub(updated_stub, stub_id=stub_filename)

    # Update the cache
    with _processed_lock:
        _processed_stubs[stub_filename] = {
            "stub": updated_stub,
            "validation": validation,
            "extraction_method": original["extraction_method"],
            "filename": stub_filename,
        }

    # Return the review form partial with updated data
    return templates.TemplateResponse(
        request,
        "partials/review_form.html",
        context={
            "stub": updated_stub,
            "validation": validation,
            "filename": stub_filename,
        },
    )
