# Remittance Stub Parsing — Current Work Plan

The current arc of work. Updated when the arc changes, not every
session. For session-by-session state, see HANDOFF.md.

---

## Goal (confirmed 2026-06-04 via /clarify)

Build all five deliverables for the remittance stub parsing portfolio
piece: extraction engine, SQLite ledger, case study (HTML+PDF),
FastAPI+HTMX demo with review queue, and synthetic stubs in four
retailer/distributor formats.

## Why this arc, why now

First published piece to demonstrate document AI / OCR → structured
data. Closes the intake loop with Deduction Recovery (shipped) and
Trade Spend Leakage (shipped). Largest capability gap in the current
portfolio.

## Business question this arc answers

How much money is hiding in your remittance PDFs that will expire
past the dispute window before anyone reconciles it?

## Scope (from /clarify)

**In scope:**
- All 5 deliverables: extraction engine, SQLite ledger, case study
  (HTML+PDF), demo + review queue, synthetic stubs
- 4 formats: Walmart, Costco, UNFI, KeHE — all native-text PDFs
- Intentionally broken stubs (mismatched amounts, unmapped reason
  codes) to exercise the review queue
- Deterministic validation: net + sum(deductions) = gross invoice
- Reconciliation against Cinderhaven SSOT (Postgres) — 864
  chargebacks, $3.4M annualized all-in trade cost
- Demo as educational walkthrough of the full reconciliation process
- Tech stack: Python, everything else decided during /ce:plan
- Deployment: Fly.io or Cloudflare, decided during planning
- Lailara design system, Economist voice, canonical Cinderhaven figures

**Out of scope:**
- OCR / scanned-image pipeline (architecture can note support, but
  not built — all synthetic stubs are native-text PDFs)
- Parsing arbitrary/unknown PDF formats (demo handles only the 4
  known synthetic formats)
- Automated dispute filing to retailer portals
- Full AP-automation / payment-processing workflow
- General-purpose document parsing engine

## Tasks

Full plan at docs/plans/2026-06-04-001-feat-remittance-stub-parsing-plan.md.
9 implementation units, executed via /ce:work.

- [x] **Pre-work:** Verify Cinderhaven canonical figures — DONE. Phase A locked: $3.4M annualized / 864 chargebacks / 36 months. Phase B (propagate edits) pending next session.
- [x] U1. Foundation — project setup, data models, configs
- [x] U2. Synthetic stub generation — FPDF2 stubs for 4 formats
- [x] U3. PDF table extraction — pdfplumber with per-format tuning
- [x] U4. LLM structured extraction — Claude API for variable line items
- [x] U5. Validation, ledger, and reconciliation
- [x] U6. FastAPI web app — skeleton, templates, HTMX, SSE
- [x] U7. Interactive demo — guided tour, free exploration, review queue
- [x] U8. Dynamic case study — report generation with WeasyPrint
- [x] U9. Design system polish and Fly.io deployment

## Definition of done for this arc

- [x] Synthetic stubs exist for all 4 formats, including intentionally
      broken ones, reconciling against Cinderhaven SSOT
- [x] Extraction engine parses all 4 formats into typed records
- [x] Deterministic validation catches mismatches and routes to review
- [x] SQLite ledger populated, reconciled against invoice/AR records
- [x] FastAPI+HTMX demo tells the full parsing → validation →
      reconciliation story as an educational walkthrough
- [x] Review queue shows flagged rows with side-by-side PDF + form
- [x] Case study (HTML+PDF) with Cinderhaven findings, ties to $3.4M annualized
- [x] All numbers match Cinderhaven canonical figures exactly
- [ ] Deployed (Fly.io or Cloudflare) with lailarallc.com subdomain

---

## Arc history

When an arc completes, archive its goal, completion date, and outcome
here. Then start a new arc above. Provides continuity without bloating
the active plan.

---

## Improvement history

Track when this project was reviewed and improved via /improve.
Each entry records what was found, what was fixed, and when to
check again.

<!-- Entries are added by /improve — don't delete this section -->
