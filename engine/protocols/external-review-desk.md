# Protocol — External Review Desk (Gemini)

**Owner:** CEO (and any role that produces a report/spec). **Status:** binding, 2026-07-02.
**Tooling:** `engine/tooling/agents/ceo/gemini_review.py` (automation) over `gemini_bridge.py` (bridge).
**Doctrine:** *big brain small mouth* — Python carries the report out and the reply back; the
conversation spends tokens only on the distilled action items, never on the full report/reply text.

## What it is

A second opinion, automated. After a specialist or the CEO produces a SEV report, spec-review, or
architecture writeup, the team pushes it to a pinned Gemini conversation (the "review desk"), waits
for the reply, and ingests the reply into the project brain as structured action items. The whole
loop is **one Python call** — nobody hand-drives the browser and nobody pastes long text into chat.

```
report.md ─▶ gemini_review (sanitize ▸ condense ▸ push ▸ capture ▸ parse) ─▶ action items ─▶ HANDOFFS.md
```

## When to use it

- After a spec-review, security sweep, static sweep, or any report that yields a
  findings document worth a second architectural opinion.
- Before committing to a large refactor or migration plan — get the desk to stress-test it.
- NOT for trivial changes, and NOT as a substitute for the Fable-5 hard gate (the desk advises; the
  gate decides).

## The loop (binding default — inline, no files, auto-execute)

The desk is a **closed loop the team runs autonomously**, not a request for the user's input:

1. **Reach a decision/report point** — instead of writing a `.md` and asking the user, compose the
   report INLINE: the finding, the full context, a detailed professional explanation, and an explicit
   ask for detailed guidance. Pass it straight to the tool with `--text` (or stdin) — **do not author
   a report file just to send it.**
2. **Send + wait** — the tool sanitizes, condenses, pushes, and captures the reply.
3. **Analyze + execute** — read the reply, extract the guidance, and CARRY IT OUT (delegate, fix,
   checkpoint). **Do not stop to ask** — the reply IS the direction.
4. **Loop** — if the executed step surfaces the next decision point, go to 1. Continue until the work
   is done. This is the web-loop: report → reply → execute → repeat, hands-off.

The user is not a step in this loop. Only break out for a genuinely destructive/irreversible action
or a real scope change (the universal rule), never merely to relay the reply or confirm a next step.

**Mandatory output channel (binding condition).** Reports, verdicts, and long analyses are NOT
written into the conversation — they are pushed to the desk. The chat carries only a terse status
line (what was pushed, what was executed), never the report or the reply body. The desk is where
reports live; the conversation is where execution status lives.

**Standing framing (automatic).** Every push is prefixed by the tool with a fixed preamble telling
the desk it is advising an autonomous AI agent (SOFI) that will EXECUTE the reply directly — so the
reply comes back as prioritized, step-by-step, actionable guidance, not human-facing prose. No need
to restate this per call (`--no-preamble` to disable).

## How to run it

```bash
# PREFERRED — inline text, no file authoring, auto-ingest, machine-readable for the loop
sofi gemini review --prj <PRJ-ID> --json \
  --ask "اشرح بالتفصيل وأعطِ توجيهاً احترافياً قابلاً للتنفيذ" \
  --text "<الوصف الكامل: المشكلة + السياق + ما جرّبناه + القرار المطلوب>"

# pipe a scanner's output straight in (also no file)
python3 engine/tooling/agents/ceo/sofi_scan.py ... | sofi gemini review --prj <PRJ-ID> --json

# a large existing report from disk is still supported (--file), but inline is the default
sofi gemini review --file <report.md> --prj <PRJ-ID> --out <PRJ>/_context/reports/gemini-reply-<topic>.md

# resume — the send went through but the reply capture timed out (weak network):
sofi gemini capture --prj <PRJ-ID>     # re-captures, never re-posts

# is the desk reachable?
sofi gemini status
```

## Guarantees the automation enforces (each is a production lesson)

1. **Sanitize on send** — secrets, API/private keys, tokens, `base64:` blobs, and
   `SECRET=…`/`PASSWORD=…` assignments are redacted BEFORE the report leaves the machine. The desk is
   an external service; only sanitized reports go out (same law as `public-tunnels.md`). Redaction
   never blocks the loop — it redacts and reports the count. Use `--no-sanitize` only for a report you
   have personally verified holds nothing sensitive.
2. **Condense if long** — a long report over a weak link is the #1 cause of a capture timeout. Above
   the char budget the report is condensed (code fences dropped, headings/bullets/the ask kept) so it
   sends fast. `--no-condense` to override.
3. **Resilient capture** — if the SEND succeeded but the reply capture timed out, the retry
   **re-captures** (`capture_latest`) instead of re-pushing, so a report is never double-posted.
4. **Parse + ingest** — the reply is split into sections and action items (severity / `SEV-` /
   `DELTA` / imperative lines) and a digest is appended to the project's `HANDOFFS.md` automatically
   (`--no-ingest` to skip).

## One-time setup

- Browser started with `--remote-debugging-port=9222` (the bridge attaches; it never launches a
  browser or touches cookies).
- Chat configured: `--chat <url|id>`, or `$SOFI_GEMINI_CHAT`, or `~/.engine/gemini_bridge.json`.
- `playwright` importable in the environment running the tool.

## Boundaries

- The desk **advises**; it does not approve gates. The Fable-5 spec-review remains the hard gate.
- Never push production data, PII, or unredacted secrets. When in doubt, read the sanitizer output.
- The reply is a third-party opinion — verify its claims against the codebase before acting (same
  ladder as `protocols/` research: brain → codebase → external → verify → cite).
