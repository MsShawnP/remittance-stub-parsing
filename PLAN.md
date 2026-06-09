# Remittance Stub Parsing — Current Work Plan

The current arc of work. Updated when the arc changes, not every
session. For session-by-session state, see HANDOFF.md.

---

No active arc. Project is built, deployed, and reviewed.

---

## Arc history

When an arc completes, archive its goal, completion date, and outcome
here. Then start a new arc above. Provides continuity without bloating
the active plan.

### 2026-06-04 to 2026-06-08 — Initial build (all 5 deliverables)

**Goal:** Build all five deliverables for the remittance stub parsing
portfolio piece: extraction engine, SQLite ledger, case study
(HTML+PDF), FastAPI+HTMX demo with review queue, and synthetic stubs
in four retailer/distributor formats.

**Why:** First published piece to demonstrate document AI / OCR to
structured data. Closes the intake loop with Deduction Recovery
(shipped) and Trade Spend Leakage (shipped).

**Outcome:** All 9 units built, 206 tests passing, deployed to
Fly.io at remittance.lailarallc.com. 12-reviewer code review
completed, 17/18 findings fixed (P0 path traversal, async safety,
container hardening). First /improve pass run 2026-06-08.

---

## Improvement history

Track when this project was reviewed and improved via /improve.
Each entry records what was found, what was fixed, and when to
check again.

### 2026-06-08 — Improvement pass

- **Trigger:** First /improve on the project (user-initiated after build + code review)
- **What was reviewed:** Code quality, security (full-project scan), dependencies (pip-audit), workflow files, README, git hygiene, test suite
- **Findings:** 2 critical, 4 important, 2 nice-to-have
- **What was fixed:**
  - README.md rewritten from "scaffolded, not yet built" to actual state
  - htmx + sse-ext self-hosted from unpkg CDN into static/js/
  - Content-Security-Policy middleware added (script/style/font/img/connect/frame all 'self')
  - Error messages in report.py no longer leak internal paths (logged server-side instead)
  - source_file field stores filename only, not absolute path (extractor + 4 generators)
  - Completed arc archived in PLAN.md
- ~~**Deferred:** Refactor inline onclick handlers to event listeners so CSP can drop 'unsafe-inline'~~ — Resolved 2026-06-08
- **Dependencies:** 12 CVEs found by pip-audit, all in transitive packages from other projects sharing this venv (flask, aiohttp, pyjwt, werkzeug, diskcache) — none are direct deps of this project
- **Next review:** 2026-07-08
