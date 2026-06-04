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

## Data & Schema

[Decisions about data sources, schemas, transformations]

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
