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

### 2026-06-05 — trade-spend-diagnostic narrative docs assumed to be "~15 string replacements" but need complete rewrites

**Attempted:** Planned to update ~15 hardcoded narrative refs in trade-spend-data-diagnostic to canonical v2 figures as simple find-and-replace (same approach that worked for the other 4 repos).

**Why it didn't work:** The v2 Postgres data changed the diagnostic's findings structurally, not just numerically. Old: "vague" = dominant category at $406K, 21.7% all-in, 3 double-dips, 18.6% recovery. New: 8 evenly-distributed categories at ~$50K each, 10.5% all-in, 0 double-dips, 44.5% recovery. Every paragraph in README, EXECUTIVE_MEMO, walkthrough, and DEFENSIBILITY encodes the old analytical narrative. String replacement would produce internally contradictory prose.

**What we tried instead:** Rebuilt workbook + validation clean (59/59), deferred narrative rewrite to dedicated session.

**Status:** Resolved. Narrative docs rewritten with waste-magnitude framing (`1a8de45`), then reconciled to workbook figures (`25107c8`).

**Tags:** trade-spend-diagnostic, scope-escalation, narrative, canonical-v2

### 2026-06-05 — trade-spend-diagnostic workbook failed to build after Postgres re-export (missing columns)

**Attempted:** Re-exported SQLite from Postgres v2 and ran build_workbook.py directly.

**Why it didn't work:** Three schema incompatibilities: (1) `stores.retailer` column doesn't exist in v2 (has `retailer_id`), (2) `trade_spend_pct_kroger` column doesn't exist in v2 sku_costs, (3) `wholesale_kroger` doesn't exist. The old SQLite had these columns from the local generation scripts; the Postgres export doesn't.

**What we tried instead:** Ran the existing `scripts/fixup_extracted_db.py` (untracked, already written for this exact purpose) which adds compatibility columns. Then removed Kroger from CHANNEL_RATE_COLS and wholesale list since v2 has no dedicated Kroger columns. Also added Kroger and Sprouts to Tab 4's channel_order so all retailers appear.

**Status:** Resolved. Lesson: check for existing fixup/migration scripts in untracked files before attempting manual fixes.

**Tags:** trade-spend-diagnostic, schema, postgres, sqlite, fixup

### 2026-06-05 — First distressed scenario run had vague deductions at 3x target ($1.1M/yr vs $400K target)

**Attempted:** Used v1's original per-retailer vague rates (walmart 0.060, whole_foods 0.070, etc.) directly as unconditional per-order probabilities.

**Why it didn't work:** v2 has ~46K orders (vs v1's different dataset), and the bimodal vague_amount averages $1,255/event. At 2,639 vague deductions the total was $3.3M/36mo ($1.1M/yr) — nearly 3x the v1 target of ~$400K/yr. The high per-event average means small rate changes have outsized dollar impact.

**What we tried instead:** Cut vague rates by ~2.7x (e.g. walmart 0.060 → 0.022) and boosted non-vague operational types (short_ship, damaged, spoilage, late_delivery) by ~1.5x to compensate. Also widened amount ranges for short_ship (0.03-0.12 → 0.05-0.18) and late_delivery (0.03 → 0.05 Walmart). Second run: 967 vague/$419K/yr, $965K total waste/yr.

**Status:** Resolved. Lesson: when adapting rates across datasets with different order counts and economics, always check dollar output after first run, not just deduction counts.

**Tags:** distressed-scenario, calibration, vague-deductions, rate-tuning

### 2026-06-05 — Narrative docs carried "10.8% structural" but 10.8% was the baseline ALL-IN rate

**Attempted:** Rewrote all narrative docs using "structural trade rate is 10.8%" — copied from cinderhaven-data README and CINDERHAVEN_CANONICAL.md baseline block.

**Why it didn't work:** The canonical baseline section says "All-in trade rate: 10.8%." The cinderhaven-data README mislabeled it as "Structural trade rate: 10.8%." The workbook correctly computes structural as 9.2% ($3,005,686 / $32,539,868). The 10.8% = structural $3.0M + baseline waste $0.48M = $3.5M / $32.5M. Every narrative doc (README, EXECUTIVE_MEMO, walkthrough) inherited the mislabel.

**What we tried instead:** Reconciliation pass — set all docs to workbook-computed 9.2% structural, added explicit all-in 12.2% framing, stated the 3-point delta as the recoverable waste.

**Status:** Resolved (`25107c8`).

**Tags:** trade-spend-diagnostic, figure-mismatch, structural-rate, all-in-rate, mislabel

### 2026-06-05 — Three repos diverged on push (URL cleanup batch on remote)

**Attempted:** Push 6 repos in dependency order after local commits.

**Why it didn't work:** trade-spend-data-diagnostic, retailer-deduction-recovery, and contract-to-cash all had URL cleanup/README standardization commits pushed to their remotes from a separate session. Local copies didn't have these. Push rejected with "remote contains work that you do not have locally."

**What we tried instead:** Pushed the 3 repos that weren't diverged. Deferred pull-rebase on the 3 blocked repos to next session.

**Status:** Open. Next session: `git pull --rebase origin main` on each, resolve conflicts, push.

**Tags:** git, push-rejected, divergence, url-cleanup, multi-repo
