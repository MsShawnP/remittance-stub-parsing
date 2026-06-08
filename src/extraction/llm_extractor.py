"""LLM-based structured extraction for remittance stubs.

Uses Claude API with tool use to extract deduction line items from
PDF text. The tool_choice is forced so the model always returns
structured data matching the DeductionEntry schema.

This module is optional — if no ANTHROPIC_API_KEY is set or the
API call fails, the pipeline falls back to pdfplumber-only extraction.
"""

import logging
import os
from decimal import Decimal, InvalidOperation
from typing import Optional

from src.models import DeductionEntry

logger = logging.getLogger(__name__)

# Model used for extraction — Haiku is fast and cheap, sufficient
# for structured data extraction from already-parsed PDF text.
_MODEL = "claude-haiku-4-5-20251001"

# Tool definition that forces Claude to return structured deduction data.
# The schema mirrors DeductionEntry fields.
_TOOL_DEFINITION = {
    "name": "record_deductions",
    "description": (
        "Record all deduction line items found in remittance stub text. "
        "Each deduction has an invoice number, reason code, description, "
        "and dollar amount."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "deductions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "invoice_number": {
                            "type": "string",
                            "description": "Invoice or reference number for this deduction",
                        },
                        "reason_code": {
                            "type": "string",
                            "description": "Reason code (e.g., '24', 'DM', 'OSD', 'PRO')",
                        },
                        "reason_description": {
                            "type": "string",
                            "description": "Human-readable description of the deduction reason",
                        },
                        "amount": {
                            "type": "string",
                            "description": (
                                "Dollar amount as a string (e.g., '1234.56'). "
                                "Always positive — deductions are stored as positive values."
                            ),
                        },
                    },
                    "required": ["invoice_number", "reason_code", "reason_description", "amount"],
                },
            },
        },
        "required": ["deductions"],
    },
}

_EXTRACTION_PROMPT = (
    "You are a data-extraction assistant. The user will provide the full text "
    "of a retailer remittance stub (payment advice). Extract every deduction "
    "line item. Each deduction has:\n"
    "- invoice_number: the invoice or reference number\n"
    "- reason_code: the short code (numeric or alphabetic)\n"
    "- reason_description: the human-readable description\n"
    "- amount: the dollar amount as a positive decimal string (no $ or commas)\n\n"
    "Use the record_deductions tool to return all deductions found. "
    "If you find no deductions, return an empty array."
)


def is_llm_available() -> bool:
    """Check whether the Anthropic API key is configured.

    Returns True if ANTHROPIC_API_KEY is set and non-empty.
    Does not validate the key against the API.
    """
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return len(key) > 0


def extract_with_llm(
    pdf_text: str,
    client: Optional[object] = None,
) -> list[DeductionEntry]:
    """Extract deductions from PDF text using Claude API tool use.

    Args:
        pdf_text: Full text extracted from the PDF (all pages concatenated).
        client: Optional Anthropic client instance. If None, creates one
                from the ANTHROPIC_API_KEY environment variable.

    Returns:
        List of DeductionEntry models parsed from the LLM response.

    Raises:
        RuntimeError: If no API key is available and no client is provided.
        RuntimeError: If the API call fails or returns unexpected format.
    """
    if client is None:
        if not is_llm_available():
            raise RuntimeError(
                "No ANTHROPIC_API_KEY set. Cannot use LLM extraction."
            )
        # Import here to avoid import error when anthropic is not needed
        import anthropic

        client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model=_MODEL,
            max_tokens=4096,
            system=_EXTRACTION_PROMPT,
            tools=[_TOOL_DEFINITION],
            tool_choice={"type": "tool", "name": "record_deductions"},
            messages=[
                {
                    "role": "user",
                    "content": f"Extract all deductions from this remittance stub:\n\n{pdf_text}",
                }
            ],
            timeout=30.0,
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {e}") from e

    # Parse the tool use response
    deductions = _parse_tool_response(response)
    return deductions


def _parse_tool_response(response: object) -> list[DeductionEntry]:
    """Parse the Claude API response to extract DeductionEntry list.

    Expects a response with a tool_use content block containing
    the record_deductions tool input.
    """
    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "record_deductions":
            raw_deductions = block.input.get("deductions", [])
            return _convert_raw_deductions(raw_deductions)

    raise RuntimeError(
        "Claude response did not contain a record_deductions tool use block. "
        f"Got content types: {[getattr(b, 'type', '?') for b in response.content]}"
    )


def _convert_raw_deductions(raw_items: list[dict]) -> list[DeductionEntry]:
    """Convert raw dicts from the LLM tool response into DeductionEntry models.

    Skips items that fail validation (e.g., non-numeric amounts) and logs
    a warning rather than crashing the whole extraction.
    """
    entries = []
    for item in raw_items:
        try:
            amount_str = str(item.get("amount", "0"))
            # Clean any stray formatting the LLM might include
            amount_str = amount_str.replace("$", "").replace(",", "").strip()
            amount = Decimal(amount_str)
            if amount < 0:
                amount = abs(amount)

            entries.append(
                DeductionEntry(
                    invoice_number=str(item.get("invoice_number", "")).strip(),
                    reason_code=str(item.get("reason_code", "")).strip(),
                    reason_description=str(item.get("reason_description", "")).strip(),
                    amount=amount,
                )
            )
        except (ValueError, KeyError, TypeError, InvalidOperation) as e:
            logger.warning(
                "Skipping malformed LLM deduction item %r: %s", item, e
            )

    return entries
