"""Extraction pipeline orchestrator.

Runs pdfplumber extraction first (free, fast, deterministic), then
optionally enhances with LLM extraction if an API key is available.
LLM results are preferred only when they find more deductions than
pdfplumber (i.e., the LLM caught items pdfplumber missed). Otherwise
pdfplumber results are preferred because they are deterministic.

If no API key is set or the LLM call fails, falls back gracefully
to pdfplumber-only extraction.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.extraction.llm_extractor import extract_with_llm, is_llm_available
from src.extraction.pdf_extractor import extract_stub
from src.models import RemittanceStub

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of the extraction pipeline.

    Wraps a RemittanceStub with metadata about which extraction
    method produced the final result and any issues encountered.
    """

    stub: RemittanceStub
    method: str  # "pdfplumber", "llm", or "pdfplumber+llm"
    llm_used: bool = False
    llm_error: Optional[str] = None
    pdfplumber_count: int = 0
    llm_count: int = 0
    warnings: list[str] = field(default_factory=list)


def extract(
    pdf_path: Path,
    force_llm: bool = False,
    skip_llm: bool = False,
    client: Optional[object] = None,
) -> ExtractionResult:
    """Run the full extraction pipeline on a PDF file.

    Steps:
    1. Run pdfplumber extraction (always).
    2. If LLM is available and not skipped, run LLM extraction.
    3. Compare results — prefer LLM only if it found more deductions.
    4. Return ExtractionResult with metadata about what happened.

    Args:
        pdf_path: Path to the PDF file.
        force_llm: If True, raise an error if LLM is unavailable
                   instead of falling back silently.
        skip_llm: If True, skip LLM extraction entirely.
        client: Optional Anthropic client (for testing with mocks).

    Returns:
        ExtractionResult with the best extraction and metadata.
    """
    path = Path(pdf_path)

    # Step 1: Always run pdfplumber first
    pdfplumber_stub = extract_stub(path)
    pdfplumber_count = len(pdfplumber_stub.deductions)

    result = ExtractionResult(
        stub=pdfplumber_stub,
        method="pdfplumber",
        pdfplumber_count=pdfplumber_count,
    )

    # Step 2: Decide whether to run LLM
    if skip_llm:
        return result

    if not is_llm_available() and client is None:
        if force_llm:
            raise RuntimeError(
                "LLM extraction requested (force_llm=True) but no "
                "ANTHROPIC_API_KEY is set and no client was provided."
            )
        result.warnings.append(
            "No ANTHROPIC_API_KEY set — using pdfplumber-only extraction."
        )
        return result

    # Step 3: Run LLM extraction
    try:
        # Get full text from the pdfplumber stub's source for LLM
        import pdfplumber as _pdfplumber

        with _pdfplumber.open(str(path)) as pdf:
            all_text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

        llm_deductions = extract_with_llm(all_text, client=client)
        llm_count = len(llm_deductions)
        result.llm_count = llm_count
        result.llm_used = True

    except Exception as e:
        logger.warning("LLM extraction failed: %s", e)
        result.llm_error = str(e)
        result.warnings.append(f"LLM extraction failed: {e}")
        return result

    # Step 4: Compare and choose the best result
    if llm_count > pdfplumber_count:
        # LLM found more — it likely caught items pdfplumber missed
        result.stub = RemittanceStub(
            retailer=pdfplumber_stub.retailer,
            check_number=pdfplumber_stub.check_number,
            payment_date=pdfplumber_stub.payment_date,
            gross_invoice=pdfplumber_stub.gross_invoice,
            net_cash=pdfplumber_stub.net_cash,
            payer_name=pdfplumber_stub.payer_name,
            deductions=llm_deductions,
            source_file=pdfplumber_stub.source_file,
        )
        result.method = "pdfplumber+llm"
        logger.info(
            "LLM found %d deductions vs pdfplumber's %d — using LLM results.",
            llm_count,
            pdfplumber_count,
        )
    else:
        # pdfplumber found same or more — keep deterministic results
        result.method = "pdfplumber"
        if llm_count < pdfplumber_count:
            result.warnings.append(
                f"LLM found fewer deductions ({llm_count}) than "
                f"pdfplumber ({pdfplumber_count}) — keeping pdfplumber results."
            )

    return result
