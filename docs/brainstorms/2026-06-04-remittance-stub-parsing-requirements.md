---
date: 2026-06-04
topic: remittance-stub-parsing
---

# Remittance Stub Parsing

## Summary

A portfolio piece that turns a stack of messy retailer remittance PDFs into a reconciled deduction ledger with dispute-window awareness. The web app is both the tool and the teacher — visitors explore the parsing, validation, and reconciliation process at whatever depth they choose, and generate a dynamic case study report from what they've seen or toggle to the complete Cinderhaven story.

---

## Problem Frame

Every dollar a retailer or distributor pays a specialty food brand arrives with a remittance advice — a PDF listing what's being paid, what's being deducted, and a reason code for each deduction. Walmart, Costco, UNFI, and KeHE each produce different formats. Nobody can act on a PDF. So today, someone in AP opens each stub and manually keys line items into a spreadsheet to figure out what got paid, what got taken, and whether the deduction was legitimate.

The operational disaster is not the deduction itself — it's the data arriving after the dispute window closes. When the manual pull is weeks behind, deductions age past the window before anyone reconciles them. The leak becomes permanent because the data arrived too late to fight. At $25M–$50M revenue with multiple distributors, this is a part-time job nobody owns and money that walks out unchallenged.

The Lailara portfolio already proves the practice can analyze structured data (SQL, CSVs, dbt models) and shows what to do with deduction data (Deduction Recovery, shipped) and how to frame trade spend (Trade Spend Leakage, shipped). It does not yet prove the practice can get data out of documents. That's the largest capability gap in the current tool story, and it's the gap this piece fills.

---

## Actors

- A1. Visitor (CFO / controller): arrives from LinkedIn, a related portfolio piece, or organic search. Wants to understand whether this kind of automation is real and relevant to their operation.
- A2. Visitor (AP clerk / ops person): recognizes the remittance formats, wants to see how the parsing handles the messiness they deal with daily.
- A3. Visitor (broker): files some disputes on behalf of the brand, wants to see how the flagging and dispute-window awareness works.

---

## Key Flows

- F1. Guided tour
  - **Trigger:** First-time visitor lands on the demo
  - **Actors:** A1, A2
  - **Steps:** Demo walks visitor through all four retailer formats in a progressive sequence — simpler stubs first, building to the broken stub that fails validation and routes to the review queue. Each step reveals a stage of the pipeline (raw PDF → extracted fields → validation pass/fail → reconciled ledger).
  - **Outcome:** Visitor understands the full process and sees both clean and failed extractions
  - **Covered by:** R1, R2, R3, R5, R6, R8

- F2. Free exploration
  - **Trigger:** Visitor skips the tour or returns to explore specific formats
  - **Actors:** A1, A2, A3
  - **Steps:** Visitor picks any of the four stubs, runs it through the parser, sees the extraction, validation, and reconciliation for that stub. Visitor controls how deep they go into the review queue.
  - **Outcome:** Visitor explores the formats they care about at their own pace
  - **Covered by:** R1, R2, R3, R5, R7

- F3. Dynamic case study generation
  - **Trigger:** Visitor has explored one or more stubs and wants the report
  - **Actors:** A1
  - **Steps:** Visitor generates a case study report reflecting the stubs they explored — reconciliation findings, deduction classification, aging vs. dispute window, recoverable dollars. Visitor can toggle to "show all" for the complete Cinderhaven story across all four formats.
  - **Outcome:** HTML report viewable in-app, downloadable as PDF
  - **Covered by:** R4, R9, R10

- F4. Review queue interaction
  - **Trigger:** A stub fails deterministic validation (amounts don't balance, reason code unmapped)
  - **Actors:** A1, A2
  - **Steps:** Failed extraction routes to the review queue. Visitor sees side-by-side PDF viewer and editable form with flagged fields highlighted. Visitor can correct the extraction or observe the escalation path.
  - **Outcome:** Visitor understands the human-in-the-loop design and why the pipeline trusts arithmetic over model confidence
  - **Covered by:** R3, R6, R8

---

## Requirements

**Synthetic stubs**
- R1. Generate synthetic remittance stubs for four retailer/distributor formats: Walmart, Costco, UNFI, KeHE — all native-text PDFs
- R2. Stubs must reconcile against the Cinderhaven SSOT in Postgres (3,363 chargebacks, ~$3.6M/yr all-in trade spend, 11.0% of scan revenue) — parsed totals must not drift from canonical figures
- R3. Include intentionally broken stubs (mismatched amounts, unmapped reason codes) that fail deterministic validation and route to the review queue
- R11. Reason codes must be correct per source — UNFI promo codes differ from KeHE codes differ from Walmart codes; incorrect codes are an instant credibility loss with AP practitioners
- R12. Stubs must be realistically ugly — multi-page, inconsistent headers, inconsistent column naming, reason codes that don't map cleanly to the ERP

**Extraction engine**
- R5. Parse all four synthetic formats into typed records (item, amount, reason code) using structured extraction
- R13. Engine is packaged as a Python module within the repo, not published to PyPI

**Deterministic validation**
- R6. Enforce arithmetic validation: `net cash received + sum(line deductions) = gross invoice amount`. If it balances to the penny and every reason code maps to a known category, the row is verified; otherwise it routes to the review queue
- R14. The trust signal is the arithmetic check, not model confidence — never display or rely on model confidence percentages

**Unified ledger**
- R15. Output a unified SQLite ledger with deductions classified by reason code
- R16. Reconcile the ledger against Cinderhaven invoice/AR records
- R17. Include aging-vs-dispute-window view showing dollars about to expire

**Demo surface**
- R7. Provide both a guided tour (progressive sequence through all four formats) and free exploration (pick any stub)
- R8. Review queue shows side-by-side PDF viewer and editable form with flagged fields highlighted
- R9. Visitor controls depth of engagement — how much process detail and review queue interaction they see
- R18. Demo must work for visitors arriving cold (from LinkedIn, another portfolio piece, organic search) — landing page provides enough context without requiring the case study first
- R19. Equal weight on visual polish, transformation aha moment, and process transparency — all three are required, no tradeoffs

**Case study**
- R4. Generate a dynamic case study report (HTML, downloadable as PDF) reflecting the stubs the visitor explored
- R10. Provide a "show all" option that generates the complete Cinderhaven story across all four formats
- R20. Recoverable dollar figure is derived from the Cinderhaven data during the build — anchored against the ~$380K/yr operational deduction waste, framing recovery, labor savings, and dispute-window forfeit
- R21. Economist voice: sober, declarative, data-forward. No marketing language, no hedging that softens a real finding
- R22. Follow the Lailara design system for all visual output

**Deployment**
- R23. Deploy with a lailarallc.com subdomain
- R24. Deployment target (Fly.io or Cloudflare) decided during planning

---

## Acceptance Examples

- AE1. **Covers R6, R14.** Given a Walmart stub where net cash + sum of deductions equals the gross invoice to the penny and all reason codes map, the extraction is auto-verified with no confidence percentage shown.
- AE2. **Covers R3, R6, R8.** Given a UNFI stub where net cash + sum of deductions does not equal the gross invoice, the extraction routes to the review queue with mismatched fields highlighted in the side-by-side view.
- AE3. **Covers R3, R6.** Given a KeHE stub with a reason code that does not map to any known category, the extraction routes to the review queue even if the arithmetic balances.
- AE4. **Covers R4, R10.** Given a visitor who explored only the Walmart and UNFI stubs, the generated case study report shows reconciliation findings for those two formats. Toggling "show all" adds Costco and KeHE findings.
- AE5. **Covers R2, R20.** The reconciled ledger totals tie exactly to the Cinderhaven canonical ~$3.6M/yr all-in trade spend figure — no drift.

---

## Success Criteria

- A CFO or controller visiting the demo understands within 60 seconds what the tool does and why it matters to them
- A visitor who completes the guided tour can articulate the three-layer value (recovery, labor, dispute-window forfeit) without reading external documentation
- The dynamic case study is compelling enough that a controller would forward it to their CFO, and the CFO would forward it to their broker
- The review queue demonstrates "we trust the math, not the model" as a visible, tangible design principle — not just a claim
- All numbers in the case study reconcile exactly against Cinderhaven canonical figures
- The piece visually matches the quality bar of the existing Lailara portfolio (design system compliance, Economist chart standards)

---

## Scope Boundaries

- No OCR / scanned-image pipeline (architecture can note support for production, not built)
- No parsing of arbitrary or unknown PDF formats — demo handles only the four known synthetic formats
- No automated dispute filing to retailer portals
- No full AP-automation or payment-processing workflow
- No general-purpose document parsing engine
- Extraction engine is not published to PyPI — portfolio code, not a distributed library
- Tech stack (libraries, web framework, deployment target) is decided during planning, not here

---

## Key Decisions

- **Deterministic validation over model confidence:** The pipeline enforces arithmetic checks and reason-code mapping as the trust signal. Model confidence percentages are never shown. This is the production-maturity differentiator and the credibility marker for practitioners.
- **No OCR pipeline for this build:** All four synthetic formats are native-text PDFs. OCR adds engineering cost without portfolio value when we control the synthetic data. Architecture can note OCR support.
- **Demo as education:** The tool is the teaching mechanism — using it reveals the complexity of remittance reconciliation. Not a tool with explanatory text layered on top.
- **Dynamic case study:** The report is generated from the stubs the visitor explored, not a static document. "Show all" gives the complete Cinderhaven story.
- **Adaptive depth:** Visitor controls how much process detail and review queue interaction they see. Guided tour for first-timers, free exploration for ops people.
- **Broken stubs required:** Intentionally broken stubs exercise the review queue with real failure modes — this is the reality, not an edge case.

---

## Dependencies / Assumptions

- Cinderhaven SSOT in Postgres is accessible and contains the invoice/AR/chargeback records needed to build synthetic stubs and reconcile the output ledger
- The 3,363 chargebacks and ~$3.6M/yr all-in trade spend figures are current and canonical (per CINDERHAVEN_CANONICAL.md)
- Existing Cinderhaven retailers (Walmart, Costco, UNFI, KeHE) have enough data to support realistic synthetic stubs per format

---

## Outstanding Questions

### Deferred to Planning

- [Affects R5][Needs research] Best PDF extraction library for native-text financial PDFs — pdfplumber vs. alternatives
- [Affects R5][Needs research] LLM extraction approach for variable line-item tables — which model, local vs. API, structured output method
- [Affects R7, R8, R18][Needs research] Web framework decision — FastAPI + HTMX vs. alternatives for the demo surface and review queue
- [Affects R23, R24][Needs research] Deployment target — Fly.io vs. Cloudflare for a Python web app with PDF processing
- [Affects R4][Technical] Dynamic PDF generation approach for the downloadable case study
- [Affects R20][Technical] Derivation of the recoverable dollar figure from Cinderhaven data — what's the plausible recovery rate against the ~$380K/yr operational deduction waste
- [Affects R7][Technical] Guided tour implementation — how the progressive sequence is structured and navigated
