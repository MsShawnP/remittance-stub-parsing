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
- Reconciliation against Cinderhaven SSOT (Postgres) — 464
  chargebacks, $5.4M all-in trade cost
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

Work in vertical slices — one section/feature end-to-end before moving
to the next. To be broken down via /ce:brainstorm and /ce:plan.

- [ ] Tasks to be decomposed during planning

## Definition of done for this arc

- [ ] Synthetic stubs exist for all 4 formats, including intentionally
      broken ones, reconciling against Cinderhaven SSOT
- [ ] Extraction engine parses all 4 formats into typed records
- [ ] Deterministic validation catches mismatches and routes to review
- [ ] SQLite ledger populated, reconciled against invoice/AR records
- [ ] FastAPI+HTMX demo tells the full parsing → validation →
      reconciliation story as an educational walkthrough
- [ ] Review queue shows flagged rows with side-by-side PDF + form
- [ ] Case study (HTML+PDF) with Cinderhaven findings, ties to $5.4M
- [ ] All numbers match Cinderhaven canonical figures exactly
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
