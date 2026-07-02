# Canonical Figure Propagation Manifest

Standing runbook for Cinderhaven trade-cost figure propagation.
One row per file:line. Correct replacements from CINDERHAVEN_CANONICAL.md
approved phrasings.

**Created:** 2026-06-04
**Source of truth:** `cinderhaven-data-platform/CINDERHAVEN_CANONICAL.md`
**Methodology:** grep across all local repos for superseded values.

---

## Approved phrasings (copy these, never re-derive)

| Context | Exact phrasing |
|---------|----------------|
| Trade context (annual) | "~$3.6M/yr all-in trade spend, 11.0% of scan revenue (trailing 52 weeks)" |
| Recoverable layer | "~$380K/yr operational deduction waste; 3,357 chargebacks (2,873 retailer + 484 distributor) over 36 months" |
| 36-mo total | "[36mo total deferred — recompute from updated SSOT]" |

---

## 1. trade-spend-data-diagnostic — REACHABLE (requires Postgres re-export)

**Status: BLOCKED — needs flyctl proxy session to re-export SQLite, rebuild workbook, then update narrative docs with actual new figures. Do NOT manually swap numbers; the workbook computes them from data.**

### Hardcoded narrative refs (update AFTER re-export + rebuild)

| File:Line | Current (stale) | Replacement | Action |
|-----------|----------------|-------------|--------|
| README.md:1 | "$1.1M of margin to operational waste" | Re-derive from rebuilt workbook | AFTER-REBUILD |
| README.md:5 | "all-in cost is 20%" | Re-derive | AFTER-REBUILD |
| EXECUTIVE_MEMO.md:9 | "spending 20%" | Re-derive | AFTER-REBUILD |
| EXECUTIVE_MEMO.md:15 | "16.7% structural", "20.4% all-in" | Re-derive | AFTER-REBUILD |
| EXECUTIVE_MEMO.md:24-32 | Breakdown table ($406K, $196K, etc.) | Re-derive | AFTER-REBUILD |
| EXECUTIVE_MEMO.md:41 | "3,581 disputes", "$296K", "18.6%" | Re-derive | AFTER-REBUILD |
| EXECUTIVE_MEMO.md:69 | "$1.1 million" | Re-derive | AFTER-REBUILD |
| walkthrough.md:6 | "all-in cost is 20.4%" | Re-derive | AFTER-REBUILD |
| walkthrough.md:47 | "20.4% actual all-in rate, $1.1 million" | Re-derive | AFTER-REBUILD |
| walkthrough.md:123 | "$29,854,750 in trailing-twelve-month wholesale sales" | Re-derive | AFTER-REBUILD |
| walkthrough.md:214 | "operational, 20.4% all-in" | Re-derive | AFTER-REBUILD |
| DEFENSIBILITY.md:162 | "~$1.13M in trailing-365 operational waste" | Re-derive | AFTER-REBUILD |
| DEFENSIBILITY.md:164-165 | "~$1.09M is addressable" | Re-derive | AFTER-REBUILD |
| validate_workbook.py:99-100 | `approx(all_in_rate, 0.217, 0.01)` | Update bounds after rebuild | AFTER-REBUILD |
| sql/README.md:114-115 | "16.7% structural + 3.8% waste = 20.4% all-in" | Re-derive | AFTER-REBUILD |
| sql/README.md:162 | "$6,103,524 (20.4%)" | Re-derive | AFTER-REBUILD |
| sql/trade_rate/all_in_trade_rate.sql:15 | "$1,967,416 (7.2%), all-in 26.1%" | Re-derive | AFTER-REBUILD |

### History/decision docs (stale figures in context — preserve as history)

| File:Line | Content | Action |
|-----------|---------|--------|
| DECISIONS.md:114-117 | Old verification figures ($5.2M/18.9%, $2.0M/7.2%, $7.2M/26.1%) | HISTORY — no change |
| DECISIONS.md:132 | "11.3% all-in" (describing the problem that was fixed) | HISTORY — no change |
| DECISIONS.md:134 | Old trade rate ranges (Walmart 18-25%, etc.) | HISTORY — no change |
| DECISIONS.md:152-155 | Old locked figures ($5,207,524, $1,967,416, $7,174,939) | HISTORY — no change |
| HANDOFF.md:16 | "11.3% all-in" (session context) | HISTORY — no change |
| HANDOFF.md:18 | "$24.6M revenue, 17.5% structural, 4.2% waste, 21.7% all-in" | HISTORY — no change |
| HANDOFF.md:68-70 | Old verification figures | HISTORY — no change |
| HANDOFF.md:96-97,99,102 | Old dollar amounts and rates | HISTORY — no change |

### Vendored cinderhaven-data (old gen scripts — stale but low priority)

| File:Line | Content | Action |
|-----------|---------|--------|
| cinderhaven-data/README.md:62 | "$7.2M (26.1%)" | VENDORED — update when submodule updates |
| cinderhaven-data/data_generation_log.md:44 | "381 events, $88k over 18 months" | VENDORED |
| cinderhaven-data/scripts/12_generate_post_audit_claims.py:20 | "18-month window" | VENDORED |
| cinderhaven-data/scripts/04b_generate_price_history.py:7,116 | "8-18 months after launch" | FALSE POSITIVE — product lifecycle timing, not data window |

---

## 2. trade-spend-leakage — REACHABLE

**Status: LOW PRIORITY — all stale refs are in vendored cinderhaven-data submodule. Dashboard queries Postgres directly (current data).**

| File:Line | Content | Action |
|-----------|---------|--------|
| data/cinderhaven-data/README.md:68 | "$7.2M (26.1%)" | VENDORED — update when submodule updates |
| data/cinderhaven-data/data_generation_log.md:44 | "381 events, $88k over 18 months" | VENDORED |
| data/cinderhaven-data/scripts/12_generate_post_audit_claims.py:20 | "18-month window" | VENDORED |
| data/cinderhaven-data/scripts/04b_generate_price_history.py:7,116 | "8-18 months after launch" | FALSE POSITIVE — product lifecycle, not data window |

---

## 3. retailer-deduction-recovery — REACHABLE

**Status: LOW PRIORITY — "18 months" refs are in data gen schema docs describing OLD generation targets. Project uses its own data pipeline.**

| File:Line | Current (stale) | Replacement | Action |
|-----------|----------------|-------------|--------|
| data/schema.md:308 | "18-month window (Dec 2024 → May 2026)" | "36-month window (Jan 2024 → Jan 2027)" | FIX |
| data/schema.md:319 | "per retailer × 18 months" | "per retailer × 36 months" | FIX |
| data/schema.md:321 | "over 18 months" | "over 36 months" | FIX |

---

## 4. contract-to-cash — REACHABLE

**Status: NO ACTION — all "18 months" references document the decision to SCOPE from 18mo to CY2025. These are historical context, not assertions.**

| File:Line | Content | Action |
|-----------|---------|--------|
| AUDIT.md:120 | "unbounded 18-month data. After scoping to CY2025" | HISTORY — documenting scope decision |
| AUDIT.md:245 | "full 18-month dataset (3,087" | HISTORY |
| DECISIONS.md:84 | "An 18-month window is unrealistic..." | HISTORY — the decision itself |
| HANDOFF.md:122 | "was unbounded 18-month window" | HISTORY |
| docs/plans/...plan.md:113 | "spans December 2024 – May 2026 (18 months)" | HISTORY — plan written against old data |

---

## 5. where-the-money-comes-from — REACHABLE

**Status: CLEAN — no stale trade-cost figures. Generic "trade spend" and "chargeback" references are contextual, not citing specific dollar amounts.**

---

## 6. short-ship-cost (150 Cases) — REACHABLE

**Status: NEAR-CLEAN — one stale table row count, explicitly marked as unused.**

| File:Line | Current (stale) | Replacement | Action |
|-----------|----------------|-------------|--------|
| docs/cost-engine-docs.md:30 | "chargebacks \| 381" | "chargebacks \| 864" (or 690 retailer-only) | LOW — cost engine uses fallback rates, not this table |

---

## 7. chargeback-prediction-model — REACHABLE

**Status: CLEAN — uses 690 retailer chargebacks (correct per canonical). No stale trade-cost refs.**

---

## 8. dimension-weight-integrity — REACHABLE

**Status: FIX NOW — 2 references cite dead 464 / $5.4M figures.**

| File:Line | Current (stale) | Replacement | Action |
|-----------|----------------|-------------|--------|
| build_spec_dimension_integrity.md:91 | "464 chargebacks" and "$5.4M all-in trade" | "3,363 chargebacks" and "~$3.6M/yr all-in trade spend, 11.0% of scan revenue (trailing 52 weeks)" | FIX |
| build_spec_dimension_integrity.md:296 | "464" and "$5.4M all-in trade / 464-chargeback canon" | "3,363" and "~$3.6M/yr all-in trade / 3,363-chargeback canon" | FIX |

---

## 9. remittance-stub-parsing — REACHABLE (this repo)

### Docs that cite stale figures as current (FIX)

| File:Line | Current (stale) | Replacement | Action |
|-----------|----------------|-------------|--------|
| portfolio_project_brief_remittance_parsing.md:44 | "$5.4M all-in trade cost" | "~$380K/yr operational deduction waste (3,363 chargebacks)" | DONE (Phase 5 + v3 update) |
| portfolio_project_brief_remittance_parsing.md:49 | "464 chargebacks / 18 months, $5.4M all-in trade cost" | "3,363 chargebacks / 36 months, ~$3.6M/yr all-in trade spend" | DONE (Phase 5 + v3 update) |
| portfolio_project_brief_remittance_parsing.md:51 | "quantify against the $5.4M base" | "quantify against the ~$380K/yr operational deduction waste" | DONE (Phase 5 + v3 update) |
| portfolio_project_brief_remittance_parsing.md:180 | "464 chargebacks, $5.4M all-in trade cost" | "3,363 chargebacks, ~$3.6M/yr all-in trade spend" | DONE (Phase 5 + v3 update) |
| portfolio_project_brief_remittance_parsing.md:189 | "canonical $5.4M" | "canonical ~$3.6M/yr" | DONE (Phase 5 + v3 update) |
| docs/brainstorms/...requirements.md:68 | "464 chargebacks, $5.4M all-in trade cost" | "3,363 chargebacks, ~$3.6M/yr all-in trade spend, 11.0% of scan revenue" | DONE (Phase 5 + v3 update) |
| docs/brainstorms/...requirements.md:96 | "anchored against the $5.4M all-in trade cost" | "anchored against the ~$380K/yr operational deduction waste" | DONE (Phase 5 + v3 update) |
| docs/brainstorms/...requirements.md:112 | "Cinderhaven canonical $5.4M all-in trade cost" | "Cinderhaven canonical ~$3.6M/yr all-in trade spend" | DONE (Phase 5 + v3 update) |
| docs/brainstorms/...requirements.md:153 | "464 chargebacks and $5.4M all-in trade cost figures" | "3,363 chargebacks and ~$3.6M/yr all-in trade spend figures" | DONE (Phase 5 + v3 update) |
| docs/plans/...plan.md:29 | "$5.4M all-in trade cost" | "~$3.6M/yr all-in trade spend" | DONE (Phase 5 + v3 update) |
| docs/plans/...plan.md:137 | "464 chargebacks / $5.4M base" | "3,363 chargebacks / ~$380K/yr recoverable base" | DONE (Phase 5 + v3 update) |
| docs/plans/...plan.md:453 | "anchored against the $5.4M base" | "anchored against the ~$380K/yr operational deduction waste" | DONE (Phase 5 + v3 update) |
| docs/plans/...plan.md:465 | "Cinderhaven $5.4M canonical figure" | "Cinderhaven canonical ~$3.6M/yr all-in trade spend" | DONE (Phase 5 + v3 update) |
| docs/plans/...plan.md:671 | "$5.4M all-in trade cost, 464 chargebacks" | "~$3.6M/yr all-in trade spend, 3,363 chargebacks" | DONE (Phase 5 + v3 update) |

### History/context docs (stale figures documented as wrong — preserve)

| File:Line | Content | Action |
|-----------|---------|--------|
| DECISIONS.md:89,97,107,109 | Supersedes documentation — describes WHY figures are wrong | HISTORY — no change |
| FAILURES.md:34,36,39,41,42 | Failure log documenting the triple-wrong discovery | HISTORY — no change |
| HANDOFF.md:14,29,76 | Session logs describing verification work | HISTORY — no change |

---

## Summary

| Repo | Status | Stale refs | Action |
|------|--------|-----------|--------|
| trade-spend-data-diagnostic | BLOCKED | 15+ narrative + validate script | Needs Postgres re-export session |
| trade-spend-leakage | LOW | Vendored submodule only | Update when submodule updates |
| retailer-deduction-recovery | FIX | 3 refs in schema.md | Fix "18 months" → "36 months" |
| contract-to-cash | CLEAN | History docs only | No action |
| where-the-money-comes-from | CLEAN | None | No action |
| short-ship-cost | LOW | 1 unused table count | Fix 381 → 864 when convenient |
| chargeback-prediction-model | CLEAN | None | No action |
| dimension-weight-integrity | FIX NOW | 2 refs in build_spec | Fix 464→3,363, $5.4M→~$3.6M/yr |
| remittance-stub-parsing | DONE | 14 refs in brief/reqs/plan | Fixed per Phase 5 + v3 canonical update |

## Follow-up checklist (per-repo sessions)

- [ ] **trade-spend-data-diagnostic**: flyctl proxy → re-export SQLite → python build_workbook.py → update all AFTER-REBUILD rows above → update validate_workbook.py bounds → git tag cinderhaven-data-v2
- [ ] **trade-spend-leakage**: update cinderhaven-data submodule to current platform HEAD
- [ ] **retailer-deduction-recovery**: update data/schema.md generation targets (3 lines)
- [ ] **short-ship-cost**: update cost-engine-docs.md chargeback table count (1 line)
