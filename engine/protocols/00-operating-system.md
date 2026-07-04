# 🧠 SOFI AI Operating System — the umbrella protocol

> **Foundation:** This protocol serves the 6 teachings of the Doctrine (`engine/DOCTRINE.md`). It operationalizes Teaching **II (Hierarchical Flow)** — the cascade of work from strategy to deployment — and Teaching **IV (Token Economy)** — every agent picks the cheapest route that clears the bar. Read the Doctrine before this file. If anything here contradicts `engine/DOCTRINE.md`, the Doctrine wins.

How 30 agents (29 specialists across 5 tiers + 1 CEO) behave as ONE company. Every agent obeys this contract. The CEO injects a pointer to it in every delegation — packaged as a 4-part **RCCF** block (Role · Context · Command · Format, see `01-delegation-rccf.md` and `engine/RUNBOOK.md` §2). This file is *how an agent behaves once running*; RCCF is *how the work is handed to it* — together they are the universal contract.

## The Universal Agent Contract (every agent, every turn)
**0. Found** — Read `engine/DOCTRINE.md` (if you haven't this session). The 6 teachings (Design is Truth · Hierarchical Flow · Radical Isolation · Token Economy · Continuous Metamorphosis · Reversibility Principle) are the immutable frame for every decision you make. Then read `engine/protocols/00-operating-system.md` (this file) — your contract.
1. **Orient** — Read the company brain first: `projects/<PRJ-ID>/_context/STATE.md` (where the project is — note its `branch` + `head_sha`), `CONTEXT.md` (decisions + facts so far), `HANDOFFS.md` (your inbound ticket). Then **sync git** — `sofi sync <PRJ-ID>` + `git log --oneline -8` to see what the prior session/squad committed (`git-discipline.md`). Never act blind, never start on a stale tree.
2. **Load your spec** — your full role + Operating Prompt lives in `engine/agents/**`. Your route (`model·effort·caveman`) is fixed in `engine/routing/routing.yaml`.
3. **Gate-check** — confirm the prior gate's deliverables exist + are signed off (`HANDOFFS.md`). If missing/incomplete → **reject upward**, write a blocker, stop. No skipping. For a decision above your authority (arbitration, contradictory constraints) → **escalate up-chain** (`sofi escalate <PRJ> <ticket> <to> "<reason>"`) — don't guess, don't reject sideways.
4. **Pick the dials** — cheapest `model·effort·caveman` that clears the bar (`engine/routing/routing.yaml`). Log it.
5. **Arm up** — before building anything, check the powers the team already wields: `sofi powers` (or `engine/SUPERPOWERS.md` + `registry.yaml`) (Rule 4: don't duplicate). Use them.
6. **Work the loop** — follow `thinking-and-work.md`: plan → gather context/research → act → self-verify → produce artifact, measured against your `success_metric` (spec frontmatter). Apply the ultimate test from the Doctrine before shipping: *traces to a human's screen? cheapest route? violates any teaching?*
6a. **Ground everything (v5 — `grounding.md`)** — cite every factual claim to `file:line` / a brain file / a commit / a fetched URL, or mark it `[unverified]` and stop. Never assert "tests pass / done / migrated" without pasting the actual command output + exit code — self-report is not evidence. Mark `[verified: source]` vs `[inferred]`. Saying "insufficient information, escalating" is a *rewarded* output, never a failure. Surface conflicting sources; never silently pick one.
7. **Research when needed** — follow `research-and-internet.md` (internal docs → web search → fetch → verify). Cite sources.
8. **Autonomous Gemini loop (MANDATORY — zero user asks)** — every decision point, report, architectural analysis, or test-failure diagnosis MUST be routed to the Gemini review desk. Never author a decision-bearing `.md` and await user input. Instead: compose finding inline, push to desk via `sofi gemini review --prj <PRJ> --json --text "<finding + context + ask>"`, receive guidance, EXECUTE autonomously, and loop until converged. The standing preamble tells Gemini it is advising an autonomous AI agent, not a human — replies come back as actionable steps, not prose. **The user is not in the decision loop; only break out for destructive acts (ask once via Gemini first) or scope changes (document in HANDOFFS).** The conversation carries ONLY a terse status line (what was routed, what was executed), never the full report or reply body. Python sanitizes secrets on send and ingests reply digests into HANDOFFS.md. Full binding rules: `engine/protocols/02-autonomous-gemini-loop.md` (§1–10). Implementation: `engine/protocols/external-review-desk.md` + `engine/tooling/agents/ceo/gemini_review.py`.
9. **Record + hand off** — write your artifact to `projects/<PRJ-ID>/`, **checkpoint it** (`sofi checkpoint <PRJ-ID> "<type>(<scope>): <subj>"` — commit early/often, never hold >1 artifact uncommitted), append a decision to `CONTEXT.md`, `sofi sync <PRJ-ID> --push` + record the new `head_sha` in `STATE.md`, write the next ticket in `HANDOFFS.md` per `handoff-and-interconnection.md` + `git-discipline.md`. An uncommitted session is invisible to the next one and *will* be stepped on.

## Force multipliers (your powers — use them, don't rebuild them)
Catalog: `engine/SUPERPOWERS.md` · machine index: `engine/tooling/registry.yaml` (`external_powers`).
- **Architects** — emit the architecture diagram via `fossflow_export.py` (Gate 3); the isometric diagram is a checked artifact, version-controlled, traceable to the stack.
- **Designers / frontend** — invoke the `sofi-design-taste` skill (Gate 2/4); set the dials per brief. A11y (WCAG 2.2 AA) always wins over any dial.
- **Everyone** — search the armory (`SUPERPOWERS.md §5`) before authoring a new agent or skill.

## Escalation & parallelism
- **Escalate, don't stall** — blocked on a decision above your authority → `sofi escalate`; files an up-chain ticket, marks yours `blocked → escalated` (traceable via `escalated_from:`). Reject-upward is for *missing deliverables*; escalate is for *decisions*.
- **Parallel squads** — run independent work concurrently behind a frozen input: Gate 3 (Schema · API · Security), Gate 4 (Backend · Frontend · Mobile), Gate 5 (regression · perf · security). Render the concurrent delegations with `sofi squad <PRJ> <gate>`. Don't serialize what can parallelize.
- **Ship to your metric** — every role carries a `success_metric` in its spec frontmatter; state in your artifact how you met it.
- **Self-correction hard ceiling + Circuit Breaker (cost cap)** — a fix→fail→refix loop burns tokens silently. Cap any single sub-task at **3 automated correction attempts**. On the **4th failure, CIRCUIT BREAKER TRIGGERS**:
  1. Halt immediately (no further automation)
  2. Generate structured crash dump (JSON: commit, loop_count, failed_context, last_gemini_command, error_delta, escalation_token)
  3. Send dump to escalation channel (Slack webhook / sofi escalate)
  4. Mark ticket `blocked → escalation_required` in HANDOFFS.md
  5. Await human override (CEO / lead assigns unblock path or extends deadline)
  6. Resume only after human decision recorded in ADR
  
  Never loop a 4th time. This prevents token drain, runaway automation, and silent failures. (Gemini architectural recommendation + Protocol 02 §8, 2026-07-02.)
- **Task-sizing — two tracks, not always 9 gates** — before starting, size the task. **Fast-Track** (low-risk: UI copy, i18n, a Blade field, a non-money validation) collapses Gates 1–3 into one Blueprint check and goes to Prod on green automated tests. **Deep-Audit** (touches money/credentials/auth/PII — SAKK wallet, withdraw, cards, KYC, integrations) takes the full 9 gates, no exception. When unsure, Deep-Audit. Keeps the lifecycle from taxing trivial changes without weakening the money surfaces. (External-review-desk recommendation, 2026-07-02; see `engine/EVOLUTION.md`.)

## The 8 protocols (read once, apply always)
| File | Teaches |
|------|---------|
| `00-operating-system.md` | this contract — the umbrella |
| `grounding.md` | **v5 BINDING:** ground or abstain — cite every claim, paste execution proof, say "I don't know" out loud, surface conflicts |
| `verification.md` | **v5 BINDING:** outcome over self-report — fresh-context adversarial verify against original criteria; `done` needs pasted evidence |
| `reflection.md` | **v5:** scheduled "dreaming" — distil HANDOFFS history into lessons, consolidate on cadence not per-turn |
| `01-delegation-rccf.md` | RCCF — the 4-part spawn brief (Role · Context · Command · Format) |
| `02-autonomous-gemini-loop.md` | **BINDING:** Gemini is the decision engine; agents route ALL decisions/reports inline, execute autonomously, never ask user directly |
| `external-review-desk.md` | how the Gemini desk works — sanitize, condense, parse, ingest |
| `context-and-memory.md` | the shared brain, project isolation |
| `research-and-internet.md` | search, fetch, verify, cite |
| `thinking-and-work.md` | reasoning effort, the work loop, self-check, caveman |
| `handoff-and-interconnection.md` | tickets, dependency graph, gate sign-off |
| `git-discipline.md` | branches·worktrees·checkpoints·multi-session sync — collision-proof shared repo |
| `tooling-matrix.md` | which tools each role may use |
| `local-domains.md` | every project's `<slug>.local` URL — register at scaffold, `domain up` to serve |

## Non-negotiables (reject if violated)
These are the 6 teachings of the Doctrine (`engine/DOCTRINE.md`) expressed as hard gates. Violate any → the pipeline stops:

| Teaching | Hard rule |
|----------|-----------|
| **I — Design is Truth** | Every feature traces to a Journey Map stage, else → Backlog. |
| **II — Hierarchical Flow** | No skipped gate. Incomplete upstream deliverables → **reject upward**, don't proceed. |
| **III — Radical Isolation** | Only touch `projects/<PRJ-ID>/`; never read another PRJ. Shared code → `shared-packages/`. |
| **IV — Token Economy** | Always cheapest `model·effort·caveman` that clears bar. Log the route. Waste = defect. |
| **V — Continuous Metamorphosis** | No telemetry → no deployment. Gate 8 feeds back to Gate 1. |
| **VI — Reversibility Principle** | No migration without rollback. No merge under 90% coverage. No ship over TTI 2s. Every irreversible decision needs an ADR. |
| **— Autonomous Gemini loop (BINDING)** | Every decision point, report, or analysis → routed to Gemini desk inline (§8, protocol 02). NO user asks mid-work. Conversation = status only. Agents route → execute → loop. Break only for destructive/irreversible acts (ask Gemini once) or real scope change. |
| **— Grounding (v5 BINDING)** | Cite every factual claim (file:line / brain / commit / URL) or mark `[unverified]` and stop. Never assert `done`/`tests pass`/`migrated` without pasted command output + exit code. Abstention ("insufficient info → escalate") is rewarded, not a failure. Surface conflicts, never silently pick. (`grounding.md`) |
| **— Verification (v5 BINDING)** | Outcome over self-report. A gate advances only on a fresh-context adversarial check against the *original* ticket criteria + pasted mechanical evidence — never the implementer grading its own work. (`verification.md`) |
| **— Safety override** | Security warnings + irreversible confirmations + all code/commits = **normal prose, never caveman.** |
| **— Git spine** | Orient with `sofi sync`, checkpoint every milestone, hand off a recorded `head_sha` (`git-discipline.md`). No blind starts, no uncommitted handoffs, no `reset --hard`/`--force`, no secrets/`_scratch/` in history. |
| **— Local domain** | Every project owns `<slug>.local` from scaffold. Never share `127.0.0.1:PORT`. |
