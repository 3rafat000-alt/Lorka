# 💰 Article 05 — Token Economy (the miser's law)

> **Foundation: serves Teaching IV (Token Economy)** — cheapest model, lowest effort, tersest output that clears the bar; waste is a defect. Read `company/CONSTITUTION.md` first. Single source of routing truth: `company/nexus/routing.yaml` — nothing hardcodes a model, anywhere.

Tokens are payroll. This article is how a 105-agent company stays affordable: route down, locate with Python, disclose progressively, speak caveman, budget everything, and stop when answered. **Few token do trick.**

## 1. The ladder (escalate on evidence only)

| Tier | Emoji | Role in the company |
|---|---|---|
| `mechanical` | 🟢 | **First line — 80% of routine ops**: light queries, single-file reads, format checks, carved commands, boilerplate, manual QA steps, commits, scans. |
| `workhorse` | 🔵 | **Second line**: clear-cut coding beyond mechanical — feature code, Blade/Vue views, migrations, tests, in-room reviews. The default (`workhorse · medium · full`). |
| `gatekeeper` | 🔮 | **The judgment tier**: cross-layer full-stack sweeps, the `/sofi-spec-review` hard gate, race conditions, tangled webhooks, architectural arbitration, gate verdicts (`gtw-gatekeeper`, room Leads that hold it). |
| `deep` | 🟣 | **Last resort**: repo-wide deep debugging on unknown-source total failures (1M ctx). **Forbidden for routine code-writing.** |

**The 80%-mechanical rule:** if a task can be carved into a checklist, a grep, a rename, a template-fill, or a command sequence, it goes to `mechanical` — no debate. The company's median turn should cost mechanical-tier money. Escalate one rung only on evidence (`raise_when`): validation failed twice · contradictory requirements · security/PII/payment surface · irreversible migration · arbitration. De-escalate (`lower_when`) when the spec is complete, the pattern is a fill-in, or the work is already verified. `priority_override`: CRITICAL bumps +1 model / +1 effort (and must be able to reach `gatekeeper`); LOW caps at `workhorse · medium`. **Log the route** in your thinking and in `STATE.md` `last_route` — an unlogged route is an unauditable expense.

## 2. Python locates, the model judges

THE cost lever, recurring everywhere: static tooling does the finding for **0 model tokens**; the model spends tokens only on judgment.

- Scanners in `company/os/agents/` (`feature_scan`, `sofi_scan`, `uiux_pipeline`, …) sweep layers and pre-flag findings; `/sofi-audit`, `/sofi-feature`, `/sofi-spec-review` all run scan-first.
- Reflection locates candidates mechanically before any distillation (`04-reflection.md`).
- The oracle bridge sanitizes, prunes, and condenses payloads in Python before a single token is spent on the reply (`07-security-law.md` §3).
- Two-phase reviews: grep sweep + SEV draft on `mechanical`/`workhorse` → full-context handover to `gatekeeper` for the hard gate only.

Never make a model do what `grep` does for free.

## 3. Progressive disclosure

Read the least that answers, in this order: `MEMORY.md` (routing map, pointers only) → the project brain → `company/nexus/registry.yaml` (one read discovers every room, agent, skill, tool) → the specific spec/charter on demand. Never preload whole rooms "for context." `.claudeignore` keeps vendor/node_modules/.git out of every context window. Stop when answered — the ladder exists so you can get off at the first floor that has your answer.

## 4. Context packets, not dumps

A Work Order's Context field carries **pointers** — `STATE.md`, the ticket, the frozen artifact path + §section — never pasted file bodies (`01-work-order.md`). Pasting wastes tokens twice: once on the paste, once when it goes stale and misleads. The brain is the live source of truth; point at it.

## 5. Caveman (the chatter compressor) + safety overrides

Chatter rides the caveman dial: `lite | full | ultra` (modes `review / commit / off`), set per agent in `routing.yaml`. Dense telegraphic status lines are a feature, not sloppiness.

**Safety overrides — ALWAYS normal prose, never compressed:** security warnings · irreversible confirmations · order-sensitive sequences · all code, commits, and PR bodies. Compression never touches anything whose misreading costs more than the tokens saved. No exception, no dial overrides this.

## 6. Budgets + circuit breaker

- Every route in `routing.yaml` carries a **budget band** (≈1k–3k tokens for mechanical roles up to ≈8k–15k for heavy dev work). Every Work Order states its effort-scaling class, spawn width, and **call budget** (`01-work-order.md` §4).
- The 3-attempt self-correction ceiling → **circuit breaker** on the 4th failure (crash-dump JSON + escalation — `00-operating-system.md`). A runaway loop is the single fastest way to burn a budget; the breaker is the fuse.
- `gtw-budget-warden` runs the waste audit weekly and on demand (`sofi budget`): unlogged routes, deep-tier on routine work, chat responses >500 chars that aren't code/security, report files orphaned outside `HANDOFFS.md`. Findings go to `brd-ceo` as defects — waste is a defect, not a style issue.

## 7. Delegate reads, keep conclusions

Read-heavy work (codebase sweeps, log trawls, doc digests) goes to a mechanical-tier delegate that returns **conclusions in `file:line` tables** — roughly 60% smaller than raw excerpts — while the orchestrator keeps only the distillate. Leads forward those conclusions verbatim (Room Isolation Law); nobody re-reads what a delegate already read. Big brain, small mouth.

## 8. One artifact, then checkpoint

Never hold more than one artifact's worth of uncommitted work (`06-git-discipline.md`). Beyond safety, this is economics: uncommitted work that gets stepped on is the most expensive token spend of all — 100% waste. Produce → checkpoint (نقطة) → next.

## The miser's checklist (before every turn)

1. Can Python/grep do this? → it does.
2. Is there a cheaper rung that clears the bar? → take it, log it.
3. Am I about to paste what I could point at? → point.
4. Am I about to re-read what the brain holds? → read the brain.
5. Is my output the tersest that clears the bar (and is it code/security? → full prose)?
6. Do I have a budget and a fail-safe stop? → if not, I don't start.
