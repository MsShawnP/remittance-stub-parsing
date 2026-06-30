# Remittance Stub Parsing — Project Context for Claude

## What this project is

Multi-format retailer/distributor remittance-advice parser that extracts
deduction data from PDFs (Walmart, Costco, UNFI, KeHE) into a unified,
classified, reconciled deduction ledger. Portfolio piece demonstrating
document AI / OCR capabilities — the intake stage that feeds the
already-shipped Deduction Recovery and Trade Spend Leakage pieces.

**Business question this project answers:** How much money is hiding in
your remittance PDFs that will expire past the dispute window before
anyone reconciles it?

## Stack and tools

- Primary language: Python
- Key packages/libraries: TBD (deciding during /clarify and /ce:plan)
- Database: SQLite (output ledger)
- Entry point: TBD
- Other tools: TBD

## Tier

Medium

## Project files

- CLAUDE.md (this file) — permanent rules and facts
- DECISIONS.md — durable choices and reasoning
- HANDOFF.md — current session state
- PLAN.md — current work arc
- FAILURES.md — things tried that didn't work

Read PLAN.md and HANDOFF.md at session start. DECISIONS.md and
FAILURES.md as relevant.

## Voice and standards

- Economist style for written deliverables: sober, declarative,
  data-forward
- Charts must be readable by non-data-scientist, non-researcher
  audiences
- No marketing voice or consultant filler ("leverage," "synergy,"
  "best-in-class," "unlock," "drive value")
- No hedging that softens a real finding

## Rules

### Honesty and judgment

- Say "I don't know" or "I can't verify this" instead of guessing.
  This applies to industry context, technical claims, what code did,
  and anything else.
- Tell me what I need to hear, not what I want to hear. If a decision
  looks wrong, say so. If code I wrote has problems, say so. Honest
  assessment, not validation.
- If a rule in this file is too vague to verify whether you're
  following it, flag it for revision rather than guessing at compliance.

### Building and proposing

- No speculative abstractions. If something isn't needed right now,
  don't build it. Helper functions get added when called by real code,
  not in anticipation. Parameters get added when there's a second use
  case, not the first.
- When proposing a tool, library, or approach, present at least two
  alternatives with tradeoffs, even if one is clearly preferred. Do
  not propose a single solution and move on. The default failure mode
  is taking the route with less friction instead of the route that
  best fits the project — challenge yourself before proposing.
- Tie proposals back to the business question this project is
  answering. If you can't connect a proposal to that question, the
  proposal is probably fluff and should be reconsidered.

### How to work the project

- Work in vertical slices, not horizontal phases. Build one feature
  end-to-end (working from input to output) before moving to the
  next. Don't build all the backend, then all the frontend — build
  one complete piece at a time.
- When a feature is working, suggest a simple test to verify it stays
  working: "This works now — want to add a quick test so it doesn't
  break later?" Don't force testing, but make it easy to say yes.
- Do not start tasks outside the current PLAN.md arc without flagging
  it to the user first.
- Do not refactor unrelated code unprompted.
- Do not rename things unless asked.

### Git branching

- Before risky or experimental changes, suggest creating a branch:
  > "This is a significant change. Want to work on a branch so we
  > can easily undo it if it doesn't work out?"
- What counts as "risky": changing how the project is structured,
  trying a new library, rewriting a working feature, anything where
  you'd say "I'm not sure this will work."
- Keep it simple: `git checkout -b experiment/short-description`
  before the change, merge back to main if it works.
- Don't require branches for small, safe changes. This is about
  protecting against losing work, not adding process.

### Scope creep detection

- Periodically check whether the current work matches PLAN.md.
  If the user has been building something not in the plan for more
  than ~15 minutes, flag it:
  > "We've been working on [thing] but it's not in the current plan.
  > Want to add it to PLAN.md, or should we finish the planned work
  > first?"
- This is a gentle nudge, not a block. The user may have a good
  reason. But new developers often drift without realizing it, and
  drift is how projects never finish.
- Also flag if the user keeps adding tasks to PLAN.md without
  completing existing ones — the plan is growing instead of
  shrinking.

## Working with PLAN.md

PLAN.md defines the current arc of work. Read it at session start.

- Mark tasks complete as they're finished, in the same commit as the
  work
- If a task is wrong-sized, in the wrong order, or no longer relevant,
  flag it rather than silently restructuring
- "Out of scope" items are decisions, not suggestions — do not pull
  them into the current arc without explicit user approval

## Session reminders

### Reminding the user to /log

Prompt the user to run /log when:

- A meaningful change just landed (file written, bug fixed, feature
  added, decision made)
- A natural pause point is reached (about to switch tasks, finished a
  chunk of work)
- Roughly 30-45 minutes have passed since the last /log and real work
  has happened since then

Format as a clearly separated note. Do not nag — one suggestion per
trigger.

### Reminding the user to /wrap

Prompt the user to run /wrap when:

- Context usage crosses 65%
- The user says anything that suggests they're stopping
- A natural milestone is reached
- 90+ minutes have passed and work is winding down

Format as a clearly separated note. Do not nag.

### Session start protocol

1. Read CLAUDE.md, PLAN.md, and HANDOFF.md
2. If HANDOFF.md's most recent entry is more than 24 hours old AND
   there are uncommitted changes, flag this — the previous session
   may have ended without /wrap
3. Briefly state the starting point from HANDOFF.md so the user
   confirms you're caught up
4. Confirm the current PLAN.md arc is still active
5. Check the Improvement History section of PLAN.md. If the project
   is overdue for an audit (see frequency guide in /improve), mention
   it: "This project is due for a review — run /improve or
   /improve audit-only when you're ready."
6. Remind the user what commands are available:
   > Quick reminder: type / to see your commands. The main ones are
   > /log (save checkpoint), /wrap (end session), and /improve
   > (review and improve the project). Run /commands for the full list.

### Suggesting commands during work

Don't wait for the user to remember commands exist. Proactively
suggest the right command at the right moment:

- User just finished a task → "Good time to /log that."
- User seems unsure what to do next → "Want to run /improve to
  see what needs attention?"
- User is about to stop → "Run /wrap before you go so your next
  session picks up here."
- User asks "what can I do?" or "what commands are there?" →
  "Run /commands to see everything available."
- Project is overdue for review → "It's been [X days] since the
  last /improve. Worth a quick /improve audit-only?"
- User just built a UI feature or fixed something visible →
  "Want to run /qa to test that in a browser?"
- User is starting a new project and hasn't challenged the idea →
  "Before building, run /office-hours to stress-test the idea."
- User has a plan but hasn't reviewed it → "Run /plan-ceo-review
  for the product check, then /plan-eng-review for the technical
  check."

Keep suggestions to one line. Don't explain the command every time —
just name it and say why now. If the user ignores the suggestion,
don't repeat it in the same session.

## Defaults

- Default to flagging gaps rather than filling with plausible-sounding
  but unverified content
- Default to short responses unless the task is substantive
- Default to asking before promoting a log entry to a DECISIONS.md
  entry
- Default to answering, not offering to answer

Never write secrets, tokens, or passwords into tracked files, READMEs, or commit messages — use environment variables and secret stores only.
