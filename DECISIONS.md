# Remittance Stub Parsing — Decisions Log

Permanent record of choices that should survive session turnover.
If a decision is reversed, strike it through and add the replacement
below — don't delete.

---

## Format

Each entry:
- **Date** — when decided
- **Decision** — one sentence, imperative voice
- **Why** — the reasoning, including what was tried and rejected
- **Scope** — what this applies to (file, chunk, deliverable, or "global")
- **Do not** — explicit anti-instructions, if any

---

## Architecture & Pipeline

### 2026-06-04 — Use deterministic validation (arithmetic check) as the trust signal, not model confidence
- **Why:** Raw LLM/OCR token confidence is unreliable on financial documents — a wrong number can return at 99% confidence. The pipeline enforces `net cash + sum(deductions) = gross invoice` and reason-code mapping. If it balances and maps, verified; if not, routes to human review.
- **Scope:** Global — applies to all extraction paths
- **Do not:** Show or rely on model confidence percentages as quality indicators

---

### 2026-06-04 — Drop the OCR/scanned-image pipeline; all four synthetic formats are native-text PDFs
- **Why:** Building a robust OCR pipeline for scanned financial documents is a different problem from native-text extraction. Since we control the synthetic stubs, OCR adds engineering cost without portfolio value. The architecture can note OCR support for production use.
- **Scope:** Global — all four stub formats
- **Do not:** Build or integrate PaddleOCR/Marker/Tesseract for this build arc

### 2026-06-04 — Demo parses only the four known synthetic formats, not arbitrary uploads
- **Why:** Handling unknown formats on first contact is a significantly harder problem. The demo proves the pipeline on realistic formats; it does not claim to be a general-purpose parser.
- **Scope:** Demo surface
- **Do not:** Accept or attempt to parse user-uploaded PDFs of unknown layout

### 2026-06-04 — Include intentionally broken stubs to exercise the review queue
- **Why:** Clean data is the fantasy. The review queue is a working feature, not a placeholder. Broken stubs (mismatched amounts, unmapped reason codes) demonstrate the real failure modes and the human-in-the-loop escalation path.
- **Scope:** Synthetic stub generation

### 2026-06-04 — Demo is an educational walkthrough, not just a technical tool
- **Why:** The audience may not know what's required to reconcile messy remittance data. The demo teaches the full process (parsing → validation → reconciliation) while proving the practice can do it.
- **Scope:** Demo surface, case study

### 2026-06-04 — Tech stack is genuinely open; best tools to make this shine
- **Why:** User wants the strongest possible portfolio piece. No sacred cows from the brief — Python is the language, everything else decided during /ce:plan based on research.
- **Scope:** Global

---

### 2026-06-04 — Use pdfplumber for PDF table extraction
- **Why:** MIT licensed, best table detection from layout geometry for financial PDFs with inconsistent headers. Visual debugging (`debug_tablefinder()`) invaluable during development. PyMuPDF is faster but AGPL-licensed (source disclosure for web apps) and weaker at table grouping. camelot-py struggles with borderless tables common in remittance stubs.
- **Scope:** Extraction engine (src/extraction/pdf_extractor.py)
- **Do not:** Use PyMuPDF (AGPL license incompatible with web app deployment)

### 2026-06-04 — Use Claude API with Pydantic structured outputs for LLM extraction
- **Why:** Schema-guaranteed output via constrained decoding — model cannot produce tokens violating the Pydantic schema. `messages.parse()` returns typed Python objects. Haiku 4.5 is cost-effective (~$2 for 500 stubs). Hybrid pipeline: pdfplumber first (deterministic, free), Claude API second for variable line-item tables.
- **Scope:** Extraction engine (src/extraction/llm_extractor.py)

### 2026-06-04 — Use FastAPI + HTMX + Jinja2 for demo surface
- **Why:** Native SSE for streaming pipeline progress. Pydantic models shared across extraction and API layers. No build step — ~5KB JS total. Side-by-side PDF viewer + editable form is snappy in HTMX where Streamlit is clunky.
- **Scope:** Demo surface (app/)

### 2026-06-04 — Use WeasyPrint for dynamic PDF reports
- **Why:** CSS Paged Media for professional print layout (page breaks, running headers/footers, page counters). SVG rendered as vectors — matches Lailara design system requirement. Jinja2 templates shared with web layer. Requires Debian-based Docker (not Alpine).
- **Scope:** Case study generation (app/routes/report.py)

### 2026-06-04 — Use FPDF2 for synthetic stub generation
- **Why:** Pure Python, zero system deps. Canvas-based API gives pixel-level control over PDF internals the parser will encounter. Intentional error injection is straightforward. ReportLab is more powerful but unnecessarily complex for fixed-layout test data.
- **Scope:** Synthetic stubs (src/stub_generator/)

### 2026-06-04 — Deploy on Fly.io (not Cloudflare Workers)
- **Why:** WeasyPrint requires pango/cairo system libraries unavailable in Cloudflare Workers/Pages. Fly.io supports custom Dockerfiles, persistent volumes for SQLite, and custom domains. `fly scale count 1` ensures single-writer SQLite integrity.
- **Scope:** Deployment (Dockerfile, fly.toml)
- **Do not:** Use Cloudflare Workers for this project

### 2026-06-04 — Reason-code mapping as YAML config per retailer
- **Why:** Follows config-as-artifact pattern from other Lailara projects (Dimension & Weight's cost_params.yml, Item Setup Form's partner schemas). Per-retailer YAML files readable by practitioners, serve as a deliverable.
- **Scope:** Config (src/config/reason_codes/)

---

## Data & Schema

### 2026-06-04 — Canonical Cinderhaven figures locked from current Postgres SSOT (option a)

- **Why:** Legacy figures ($5.4M / 464 chargebacks / 18 months) were wrong on all three counts. 464 was a misquoted per-channel deduction count from the deduction-recovery project (DPI Northwest's deductions), not total chargebacks. $5.4M was from a pre-May-2026 data seed, superseded by a May 2026 regen ($7.2M), then superseded again by the current Postgres regen ($3.4M annualized). "18 months" was always 36 months. Verified by querying cinderhaven-db Postgres directly on 2026-06-04.
- **Scope:** Global — all references to Cinderhaven trade cost, chargeback count, and time window
- **Canonical values:**
  - All-in trade cost: $3.4M annualized / $10.3M over 36 months (structural trade + operational waste excl promo_billback)
  - Rate: ~10.8% of trailing-52w scan revenue ($32.5M)
  - Chargebacks: 864 (690 retailer + 174 distributor, gross = net, no reversals)
  - Window: 2024-01-01 to 2027-01-02 (36 months)
  - EBITDA check: plausible (13.7% trade + 11% EBITDA = 24.7%, leaves 75.3% for COGS+SGA)
- **Do not:** Use $5.4M, $7.2M, 464, or "18 months" anywhere. All are dead.

### 2026-06-04 — All-in trade cost definition: structural + operational waste (excl promo_billback)

- **Why:** Matches the trade-spend-data-diagnostic methodology exactly. Structural = AVG(trade_spend_pct) × trailing-52w scan revenue per channel. Operational waste = trailing-365 deductions excluding promo_billback (already captured in structural rates — including it would double-count). Chargebacks (separate table) overlap with deduction types and are NOT added to all-in.
- **Scope:** Global — any computation or citation of "all-in trade cost"
- **Do not:** Add chargebacks on top of all-in. Do not include promo_billback in operational waste.

### 2026-06-04 — Trade-spend-data-diagnostic SQLite export is stale; needs re-lock in a separate session

- **Why:** The Postgres data was intentionally regenerated after the May 2026 SQLite export. Trade_spend_pct values dropped ~50% (e.g. Walmart 21.5% → 12.0%), chargebacks went from 3,441 → 864, deductions from 7,837 → 15,898. The diagnostic's locked $7,174,939 / 26.1% no longer matches the SSOT.
- **Scope:** trade-spend-data-diagnostic project (separate repo)
- **Do not:** Cite the diagnostic's old numbers ($7.17M, 26.1%) as current

---

## Visualization

[Chart conventions, palette decisions, interactivity choices]

---

## Output Formats

[Decisions about deliverable formats, structure, organization]

---

## Writing & Voice

[Voice, style, terminology decisions specific to this project]

---

## Reversed / Superseded

When a decision is overturned:
1. Strike through the original entry above (don't delete)
2. Add a new entry below with the replacement decision
3. Note the link in both directions

This preserves the history of why something is the way it is.
