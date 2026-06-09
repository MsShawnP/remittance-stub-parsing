# Remittance Stub Parsing

**Live:** https://remittance.lailarallc.com

Multi-format remittance-advice parser that extracts deduction data from retailer and distributor PDFs into a unified, classified, reconciled deduction ledger. Covers Walmart, Costco, UNFI, and KeHE — the four formats that account for the majority of specialty food trade spend. Flags arithmetic mismatches and unmapped reason codes for human review before they age past the dispute window.

## Cinderhaven context

Built on the Cinderhaven synthetic dataset — a ~$25M specialty food brand, 50 SKUs across 5 product lines and 6 contracted retailers. Data is synthetic; methodology and deliverables are real.

## What it does

- Hybrid extraction pipeline: pdfplumber (deterministic, free) runs first; Claude API (LLM, structured output via forced tool_choice) runs second when an API key is available. Pipeline picks whichever found more deductions.
- Deterministic validation: net cash + sum(deductions) = gross invoice. If it doesn't balance, the stub routes to a human review queue — no model confidence scores involved.
- Reason-code classification against per-retailer YAML configs. Unmapped codes get flagged.
- SQLite ledger with Decimal-as-text for penny-exact monetary storage.
- Reconciliation against Cinderhaven SSOT: 864 chargebacks, $3.4M annualized all-in trade cost, 36-month window.
- Interactive demo with guided tour (SSE streaming), free exploration, and a review queue with side-by-side PDF viewer + editable form.
- Dynamic case study (HTML + PDF via WeasyPrint) with Cinderhaven findings.

## Stack

- Python 3.12+
- pdfplumber — PDF table extraction from native-text PDFs
- anthropic — Claude Haiku 4.5 for structured LLM extraction
- Pydantic — data models and validation
- FastAPI + Uvicorn — web server
- Jinja2 + HTMX + SSE — templates and interactivity (no build step)
- sse-starlette — server-sent events for streaming pipeline progress
- aiosqlite — async SQLite access
- WeasyPrint — CSS Paged Media PDF report generation
- FPDF2 — synthetic test stub generation
- PyYAML — per-retailer reason-code configs
- Fly.io — deployment (Docker, pango/cairo for WeasyPrint)

## Data contract

**Canonical baseline:** 50 SKUs · 5 product lines (AS·PS·SC·DG·SB) · 6 retailers (Walmart·Costco·Whole Foods·Sprouts·Kroger·Regional Group) · 10 channels (6 retail + UNFI·KeHE·DPI + DTC)

Reconciliation uses the canonical 864 chargebacks and $3.4M annualized all-in trade cost from cinderhaven-data-platform.

## Run

```bash
git clone https://github.com/MsShawnP/remittance-stub-parsing.git
cd remittance-stub-parsing
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
pip install -e .

# Generate synthetic test stubs
python -c "from src.stub_generator import generate_all_stubs; from pathlib import Path; generate_all_stubs(Path('stubs'))"

# Run the app
uvicorn app.main:app --reload

# Run tests
pytest
```

The app works without an `ANTHROPIC_API_KEY` — pdfplumber handles extraction alone. Set the key to enable the hybrid LLM pipeline for better results on variable line-item tables.

---

Built by [Lailara LLC](https://lailarallc.com) — data hygiene and analytics consulting for specialty food brands scaling into national retail.
