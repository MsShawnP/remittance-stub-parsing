# Remittance Stub Parsing — Failure Log

What was attempted that didn't work, why it didn't work, and what was
tried next.

Lower bar than DECISIONS.md — capture failures even when they didn't
produce a durable rule. The whole point: future-you (or future-Claude)
shouldn't re-attempt dead ends because the lesson got lost.

---

## Format

### YYYY-MM-DD — [One-line failure description]

**Attempted:** [What was tried]

**Why it didn't work:** [Concrete reason, not "it broke." If the
failure mode was technical, name the specific issue. If the failure
mode was scope or approach, name that.]

**What we tried instead:** [The next attempt, which may also have
failed and may have its own entry below]

**Status:** Resolved / open / abandoned

**Tags:** [keywords for future text-search — e.g., "rendering, pandoc,
quarto" or "scope, scrollytelling, decoration"]

---

## Entries

### 2026-06-04 — Legacy "464 chargebacks / $5.4M / 18 months" triple was wrong on all three counts

**Attempted:** Used figures from the portfolio_project_brief_remittance_parsing.md as canonical Cinderhaven numbers: 464 chargebacks, $5.4M all-in trade cost, 18-month window. These propagated into PLAN.md, requirements doc, and implementation plan.

**Why it didn't work:**
- **464** was DPI Northwest's deduction count from the deduction-recovery project's `frontend/public/json/summary.json` — a per-channel figure from a different data pipeline, misquoted as "total chargebacks." Actual chargeback count from SSOT: 864.
- **$5.4M** was from a pre-May-2026 data seed. Superseded twice: first to $7.17M (May 2026 regen), then to $3.4M annualized (current Postgres). The trade_spend_pct values in sku_costs were cut ~50% between regens.
- **18 months** was always 36 months (2024-01 to 2027-01). No version of the data ever covered only 18 months.
- The $7.2M / 381-391 range from the doc review was also wrong — 381-391 doesn't match any definition against any data version.

**What we tried instead:** Queried cinderhaven-db Postgres directly, replicated exact trade-spend-diagnostic methodology, locked canonical figures at $3.4M / 864 / 36 months.

**Status:** Resolved. Phase A (verify) complete. Phase B (propagate edits to this repo's docs) pending next session.

**Tags:** canonical-figures, cinderhaven, chargebacks, trade-cost, data-drift, misquote
