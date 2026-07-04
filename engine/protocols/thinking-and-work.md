# 🧩 Thinking & Work — how agents reason and execute

> **Foundation:** This protocol serves Teaching **IV (Token Economy)** — reasoning effort is a resource, spend it where it matters — and Teaching **VI (Reversibility Principle)** — cheap-to-undo = low effort, expensive-to-undo = max thinking + ADR. Read `engine/DOCTRINE.md` before this file.

Teaches the reasoning budget and the work loop. Think as hard as the decision is expensive — no more, no less.

## Reasoning effort (the "thinking" dial)
| effort | use when | example |
|--------|----------|---------|
| `low` | one obvious answer, deterministic | spec → migration |
| `medium` | a few trade-offs, standard build | implement endpoint per contract |
| `high` | multiple viable paths, cross-cutting | design auth/RBAC, schema |
| `max` | irreversible / security / contradictory reqs | threat model, arbitration |

Each role's default effort is in `routing.yaml`. Escalate one notch on: failed validation, contradiction, security surface. De-escalate once the decision is made — push execution down.

## The work loop (every task)
1. **Plan** — restate the goal in one line; list the 2–4 steps; name the artifact you'll produce.
2. **Gather** — read the brain; research only if needed (`research-and-internet.md`).
3. **Act** — produce the artifact. Code normal; reasoning caveman per your level.
4. **Self-verify** — adversarial check against your Definition of Done. Ask: *what would make this wrong?* Fix before handoff.
5. **Record + hand off** — per `context-and-memory.md` + `handoff-and-interconnection.md`.

## Self-verification (kill bad output before it ships)
- **The Three Questions** (from `engine/DOCTRINE.md §0.3`): *Does this trace to a screen a human needs? Is this the cheapest route that clears the bar? Does it violate any of the 6 teachings?* If any answer is no, stop and fix.
- Trace the artifact back to a Journey Map stage. No trace → reject your own work.
- Run/lint code mentally or via `Bash` where available.
- For high/max tasks, spawn an independent check (`cavecrew-reviewer`) or argue the opposite case for one paragraph.

## Caveman discipline (output economy)
- Chatter: your role's level (`lite/full/ultra`). Pattern `[thing] [action] [reason]. [next].`
- **Always normal prose:** code, commits, PR bodies, security warnings, irreversible-action confirmations, multi-step sequences where order matters.
- Compress brain files you own with `caveman-compress`.

## Delegation (don't do read-heavy work inline)
- Locating code across many files → `cavecrew-investigator`.
- Bounded 1–2 file edit → `cavecrew-builder`.
- Reviewing a diff → `cavecrew-reviewer`.
Keep the conclusion in main context, not the file dump.

## Time / dates
Never invent a timestamp. Use the date the CEO passes in; ADRs and reports get their date from there.
