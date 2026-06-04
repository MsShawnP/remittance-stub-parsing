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
