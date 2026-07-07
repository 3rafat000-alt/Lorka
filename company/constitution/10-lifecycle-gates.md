# 🚪 Article 10 — Lifecycle Gates (the 9 gates)

> **Foundation: serves Teaching II (Hierarchical Flow)** — work cascades gate by gate, none skipped — **and Teaching V (Continuous Metamorphosis)** — Gate 8 closes the loop back into Gate 1. Read `company/CONSTITUTION.md` first. Machine-readable twin: `company/nexus/gates.yaml` (owner, entry criteria, exit bar, artifacts — `sofi gate-check` validates against it). `/sofi-gate` runs the check-and-advance ritual.

## The 9 gates (no skip, ever)

| # | Gate | Trigger (entry) | Owner room | Output (artifacts) | Exit bar |
|---|---|---|---|---|---|
| 0 | **Inception** | An idea worth a project; `new-project.sh` scaffold | 01-strategy | Blueprint + Problem Statement + local domain registered | Project charter exists · `<slug>.local` listed in `STATE.md` |
| 1 | **Discovery** | Gate 0 tagged; problem statement frozen | 02-research | Personas + Journey_Map (Mermaid — the Design Truth) | Answers *what the user wants* and *what blocks them* — evidence-grounded, cited |
| 2 | **Solution Design** | Journey Map frozen | 03-design | Prototype_Spec (1:1 journey mapping) + Content_Strings.json | WCAG 2.2 AA matrix passes · every screen traces to a journey stage · **freeze** (owned by `dsn-lead`) |
| 3 | **Architecture** | Prototype frozen | 04-architecture (+ 08-data, 09-security) | Schema + ERD + OpenAPI + Tech_Stack + Threat_Model + integration plans | Schema ↔ screens traceable · migrations reversible · threat model signed · journey-less features rejected here → Backlog |
| 4 | **Build** | Gate-3 bundle frozen (`arc-lead` assembles) | 05-backend · 06-frontend · 07-mobile in parallel worktrees (+ 08-data) | Code assets + tests, per frozen contract | OpenAPI + Journey Map = single truth · all states built · leads gate-merge at close |
| 5 | **Quality** | Build merged to `prj/<PRJ>` | 10-quality (the gatekeeper room) | Test reports + Design Audit (built vs frozen prototype) | ONE PASS/BLOCK verdict (`qa-lead`) · crit/high fixed · coverage > 90% · perf pass (TTI < 2s) · pass^k on money/auth/PII paths |
| 6 | **Staging / UAT** | Quality PASS | 11-devops | Staging URL + UAT log | UAT pass · pass^k re-run on critical paths |
| 7 | **Production** | UAT signed | 11-devops | Prod confirmation + **tested** rollback script | Blue/Green healthy · rollback rehearsed (`ops-release-manager` owns the way back) |
| 8 | **Observe** | Prod live | 12-observability | Perf/SLO report + journey-drop-off insights + backlog | SLO breach auto-files an issue → **re-enters Gate 1** (formal re-open by `obs-insights-analyst`) |

**Boardroom accountability spans:** `brd-cpo` answers for Gates 0–2 · `brd-cto` for Gates 3–4 · `brd-cqo` for the Gate-5 verdict · `brd-ceo` for the whole lifecycle. Room 09-security holds the veto at every gate (Article 07).

## Gate discipline (binding)

- **Domain first.** Every project gets `<slug>.local` at scaffold (`sofi domain register`, auto-run by `company/os/bin/new-project.sh`); the first squad that serves the app runs `sofi domain up <PRJ>`. Never a bare `127.0.0.1:PORT` — the clean URL is the project's public face, set before any code exists (Teaching I). URL + port live in `STATE.md` (`local_domain` / `local_port`).
- **No skip.** `sofi_tools.gates.validate_no_skip()` — gate numbers move monotonically, never jump more than +1. Loop-backs are allowed (and reported): quality can bounce work to build; observe re-opens discovery.
- **Advance = two layers.** A gate advances only on (1) `sofi gate-check` mechanical pass — artifacts exist at expected paths, evidence blocks present, no boundary violations — and (2) `gtw-gatekeeper`'s fresh-context adversarial verdict against the gate's ORIGINAL exit bar (Article 03 V1+V2). The implementer never grades itself; the oracle desk advises but never approves (Teaching VII boundary).
- **Journey-less → Backlog.** A feature that traces to no Journey Map stage is rejected at Gate 3 and parked in the Backlog — untruth does not enter architecture (Teaching I).
- **Tag at close.** `sofi gate-tag <PRJ> <N>` → `<PRJ>-gate<N>-done`, an immutable restore point per gate (Article 06 §8). Parallel worktrees merge at close via `sofi gate-merge`, never before.
- **Two tracks.** Fast-Track collapses Gates 1–3 into one Blueprint check for low-risk work; Deep-Audit (money/credentials/auth/PII) takes all 9, no exception; unsure → Deep-Audit (Article 00).
- **SLO breach re-opens Gate 1.** A Gate-8 breach or journey drop-off is not a hotfix errand — it auto-files an issue that formally re-enters Discovery, and the incident post-mortem's action items become Gate-1 tickets (incident runbook: rollback first, blameless post-mortem into `DECISIONS.md`). The loop is the company (Teaching V).

## Parallelism at the gates

Squads fan out ONLY behind a frozen input, each in its own worktree (`sofi squad <PRJ> <gate>` renders the delegations):
- **Gate 3:** schema (`dat-*`) · API (`arc-api-architect`) · security (`sec-threat-modeler`) — behind the frozen prototype.
- **Gate 4:** backend · frontend · mobile rooms — behind the frozen Gate-3 bundle; no engineer waits on another, only the contract must be frozen.
- **Gate 5:** automation · manual · perf · pentest dimensions — behind the merged build.

Never fan out the sequential phases of one ticket (Article 01 §4).
