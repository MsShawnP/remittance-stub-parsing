# Remittance Stub Parsing — Handoff Log

Session-by-session state. Updated by /log mid-session and /wrap at
session end.

For durable choices, see DECISIONS.md.
For the current work arc, see PLAN.md.
For things that didn't work, see FAILURES.md.

---

## 2026-06-05 — Guard verified, artifact audit clean, trade-spend diagnostic partially rebuilt

**Started from:** Session interrupted last night mid-commit. Needed to verify guard, audit rendered artifacts, rebuild trade-spend-diagnostic.

**Did:** Confirmed all 5 commits landed (nothing to redo). Verified freeze guard passes against live Postgres (GUARD GREEN, exit 0). Audited 6 shipped repos for stale rendered artifacts — no trade-cost figures baked in. Rebuilt trade-spend-data-diagnostic: re-exported SQLite from Postgres v2, fixed schema gaps (Kroger column, retailer_id compatibility), rebuilt workbook, recalibrated validation (59/59 pass). Identified contract-to-cash og:meta staleness. Confirmed "150 cases" = short-ship-cost. Confirmed retailer-deduction-recovery uncommitted changes don't conflict with canonical fix.

**State:**
- 4 doc/SSOT repos: committed, guard green, ready to push
- trade-spend-data-diagnostic: workbook + validation clean, code fixes applied, but 5 narrative docs still have old figures (README, EXECUTIVE_MEMO, walkthrough, DEFENSIBILITY, cinderhaven-data/README) — UNCOMMITTED
- contract-to-cash: og:meta fix identified, not applied
- This repo (remittance-stub-parsing): clean, no pending changes

**Next:** Two follow-up sessions:
1. trade-spend-data-diagnostic narrative rewrite — rewrite 5 docs with v2 figures (workbook/data is clean, only prose). Commit.
2. contract-to-cash og:meta fix — update index.html meta tags. Quick commit.
3. Push all 6 repos in dependency order (cinderhaven-data-platform first).
4. Then start U1 build in this repo.

---

## 2026-06-04 — Phase A canonical figures verified and locked

**What changed:** Queried cinderhaven-db Postgres SSOT directly (via flyctl proxy). Verified all-in trade cost, chargeback count, and data window. Found that legacy figures ($5.4M / 464 / 18 months) were wrong on all three counts. Also found that the May 2026 diagnostic figures ($7.17M / 26.1%) are stale — Postgres was regenerated with different seed_config.py parameters (trade_spend_pct values dropped ~50%).

**Locked canonical figures:**
- All-in trade cost: $3.4M annualized / $10.3M over 36 months / $3.5M trailing-52w
- Rate: ~10.8% of trailing-52w scan revenue ($32.5M)
- Components: structural trade ($8.8M/36mo) + operational waste ($1.4M/36mo, excl promo_billback)
- Chargebacks: 864 (690 retailer + 174 distributor, no reversals)
- Window: 2024-01-01 to 2027-01-02 (36 months, not 18)
- EBITDA check: plausible (24.7% trade+EBITDA, 75.3% COGS+SGA)

**What 464 actually was:** DPI Northwest's deduction count in the deduction-recovery project's summary.json. Misquoted as "total chargebacks" in the remittance brief.

**State:** Phase A (verify + report) complete. DECISIONS.md and FAILURES.md updated. PLAN.md pre-work task marked done, stale figures replaced. No code yet.

**Phase B (propagate) — first action next session:**
1. Grep this repo for $5.4M / 464 / "18 month" / $7.2M / 7,174,939 — print all hits, replace confirmed matches in: portfolio brief, requirements doc, plan doc, PLAN.md scope section
2. Do NOT edit other repos — but these external pieces cite stale figures and need separate sessions:
   - trade-spend-data-diagnostic (re-export SQLite, re-lock all 15+ hardcoded refs)
   - dimension-weight-integrity (cites "464 chargebacks" and "$5.4M")
   - Possibly: deduction-recovery, contract-to-cash, where-the-money-comes-from
3. Open question: headline number for case study copy — "$3.4M annualized" vs "$10.3M over 36 months" vs trailing-52w "$3.5M"
4. After Phase B propagation, run /ce:work to start U1

**Next concrete action:** grep + replace stale figures in this repo (Phase B), then /ce:work for U1.

---

## 2026-06-04 17:35 — Project initialized

**Started from:** New project setup via /new-project.

**Did:** Created repo, set up CLAUDE.md/DECISIONS.md/HANDOFF.md/PLAN.md/
FAILURES.md, configured project structure. Brainstorm brief already
exists at portfolio_project_brief_remittance_parsing.md.

**State:** Foundation in place. Stack set to Python (specific libraries
TBD). Ready for /clarify to scope the work.

**Next:** Run /clarify to reach 95% confidence on requirements, then
/ce:brainstorm and /ce:plan.

---

## 2026-06-04 17:50 — /clarify completed

**What changed:** Project scaffolded and /clarify completed. All five deliverables confirmed, scope boundaries locked down, five architecture decisions recorded.

**Why:** Need 95% confidence on requirements before brainstorm and planning. Confirmed all 5 deliverables required, dropped OCR pipeline, scoped demo to 4 known formats only, confirmed broken stubs for review queue, confirmed demo as educational walkthrough.

**State:** Scaffold complete (git, GitHub remote, all state files). PLAN.md has confirmed goal, scope, and definition of done. DECISIONS.md has 5 architecture decisions. No code yet. Tech stack is Python; all libraries and frameworks TBD.

**Next:** Run /ce:brainstorm to spec out architecture and tool choices.

---

## 2026-06-04 19:15 — /ce:brainstorm + /ce:plan completed, doc review done

**What changed:** Full requirements doc written (docs/brainstorms/), 9-unit implementation plan written (docs/plans/), tech stack decided via research agents, doc review applied 3 auto-fixes and surfaced 21 findings (2 at P0).

**Why:** Completing the Medium-tier workflow: /clarify → /ce:brainstorm → /ce:plan. Plan now defines the full build from foundation through deployment with researched tech choices.

**State:** Plan complete at docs/plans/2026-06-04-001-feat-remittance-stub-parsing-plan.md. 9 implementation units (U1-U9). Tech stack decided: pdfplumber, Claude API + Pydantic, FastAPI + HTMX + Jinja2, WeasyPrint, FPDF2, Fly.io. No code yet. Two P0 findings from doc review need attention before implementation:
1. **CRITICAL: $5.4M figure may be stale.** Feasibility reviewer found cinderhaven-data README shows $7.2M (26.1%) all-in trade cost and ~381-391 chargebacks, not $5.4M/464. Must verify against current Postgres SSOT and update plan, PLAN.md, requirements doc, and brief before U1.
2. R24 in Requirements section should preserve origin's open framing (Fly.io decision is correctly documented in Key Technical Decisions section).
3. SSE requires sse-starlette package (not built into FastAPI) — add to dependencies in U1.

**Next:** Start new session. First action: verify Cinderhaven canonical figures against current SSOT (query Postgres), update all docs with correct numbers, then run /ce:work on the plan.

---
