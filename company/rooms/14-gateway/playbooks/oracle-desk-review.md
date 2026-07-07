# Playbook — Oracle Desk Review (sanitize → condense → push → capture → parse → ingest → act)

> Owner: `gtw-external-reviewer`. The room's other standing procedure and its sharpest recurring job — operationalizing Teaching VII (the Autonomous Oracle Loop): decisions route to an external AI oracle, not to a human, and the loop doesn't stop until the reply is analyzed and executed. Full mechanics: `company/os/oracle/GEMINI_LOOP_ARCHITECTURE.md`; sanitization law: `company/constitution/07-security-law.md` §3.

## When to run this

- A Teaching-VII decision point: any binding choice the company would otherwise be tempted to ask a human about mid-task.
- `gtw-gatekeeper` defers a money/auth/PII-stakes gate verdict for a family-diverse second mind (`playbooks/gate-advancement.md` step 6).
- Any room's Lead wants a second architectural opinion on a report or spec worth one, before committing to a direction.
- `brd-arbiter`'s arbitration protocol routes a money/auth/PII-stakes UNKNOWN to the desk instead of ruling on a coin-flip.

## Steps

### 1. Confirm this is a genuine decision point, not routine uncertainty
The desk is a resource, not a rubber stamp for every "I'm not 100% sure." Ask: is this a binding choice, a stakes-worthy verdict, or a report someone explicitly wants a second mind on? If it's a normal judgment call inside a role's own mastery, it doesn't reach the desk — that's just the role doing its job.

### 2. Compose the report inline — no `.md` authoring first
Per the binding loop rule (`CLAUDE.md`'s external review desk section): the report is composed **inline**, in the conversation, not drafted as a standalone file first. Include: the situation, the specific ask, and enough context (frozen artifact excerpts, the exact `exit_bar` clause in question, the disputed positions if this is an arbitration input) for a model with zero shared session context to actually answer.

### 3. Sanitize — default on, every time
```bash
sofi gemini review --prj PRJ-XXXX --json --text "<inline report + context + ask>"
```
`--no-sanitize` is never passed without an explicit, logged reason (Article 07 §3) — the sanitizer redacts keys, secrets, and `.env`-shaped content before a byte leaves the machine. Read the payload once for content, once — separately — hunting only for what shouldn't cross the wire; the two passes are not the same read done twice, they have different jobs.

### 4. Condense — default on, unless the ask is already short
Condensing keeps the send weak-network-safe and keeps the receiving model's read cheap. `--no-condense` is reserved for genuinely short asks where condensing would strip meaning rather than trim filler.

### 5. Push and wait
The command sends, waits up to `--timeout` (default set in `gemini_review.py`), and either returns the reply inline or times out.

### 6. Timeout → resume, never re-send
```bash
sofi gemini capture --prj PRJ-XXXX --json
```
`sofi gemini capture` resumes the SAME conversation rather than re-posting the report — a duplicate send doubles the sanitize-review surface area for zero benefit and risks two independent replies landing out of order. If capture itself needs a health check first:
```bash
sofi gemini status
```

### 7. Parse the reply into sections + action items
The captured reply is parsed into discrete sections (the desk's read of the situation) and explicit action items (what it recommends doing) — never left as an undifferentiated wall of text. This is what makes the next step ("analyze and execute") possible without another model pass just to extract structure.

### 8. Ingest the digest into `HANDOFFS.md`
```bash
# gemini_review.py --prj PRJ-XXXX handles ingestion automatically unless --no-ingest was passed
```
The digest lands as a ticket-shaped entry in the project's `_context/HANDOFFS.md` — durable, git-spined, grep-able by `sofi brain-query` — not left to live only in a chat transcript that disappears with the session.

### 9. Analyze and execute — binding, autonomous, no stopping to ask
Per Teaching VII: **Work → Report → Oracle → Execute → Loop.** Once the digest is ingested, analyze it and act on it in the same turn — do not surface it to a human and wait. The only exception:

### 10. Destructive/irreversible action items break the loop
If an action item itself is destructive or irreversible (a schema drop, a prod deploy, a credential rotation, a force-anything), the loop breaks here: write the ADR first (`DECISIONS.md`, citing the oracle's advice as input, not as the decision itself), then ask the human. Every other action item — a report revision, a design adjustment, a routing correction — executes autonomously.

### 11. The desk advises; it never approves
No matter how confident or specific the oracle's reply, it does not clear a gate, tag a release, or override `gtw-gatekeeper`'s verdict. A glowing oracle response on a Gate-5 coverage question still needs `sofi gate-check` to actually show ≥90%. The desk sharpens a decision; `gates.yaml`'s `exit_bar` and the mechanical checks are what clear it.

### 12. Checkpoint
```bash
sofi checkpoint PRJ-XXXX "chore(oracle): gate-<N> desk review ingested — <one-line digest summary>"
```

## Worked example — money-stakes gate deferral

```
gtw-gatekeeper: Gate-5 exit_bar §"crit/high fixed" — deep_audit track, payment surface touched.
                Deferring to oracle desk (family-diverse judge required, Article 03 V2).
gtw-external-reviewer: sanitize (redacted 2 API-key-shaped strings) → condense →
                        sofi gemini review --prj PRJ-0007 --json --text "..."
                        → captured reply → parsed: 1 section, 2 action items
                        → ingested TKT-088 into HANDOFFS.md
                        → action item 1 (add idempotency key check) — non-destructive, executed
                        → action item 2 (rotate the exposed test key) — destructive/irreversible,
                          ADR-014 written, brd-cso asked before rotating
gtw-gatekeeper: rules Gate-5 exit_bar §"crit/high fixed" PASS, citing action item 1's fix + the
                oracle desk's second-mind confirmation as supporting (not deciding) evidence.
```
