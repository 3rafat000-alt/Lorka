# Protocol — /sofi-spec-review · Cross-Layer Deep Audit (Single Source of Truth)

> **Status: binding doctrine (carved 2026-07-01).** The steel safety-valve for every
> SAKK interface, wallet, and database surface. The runtime skill `.claude/skills/sofi-spec-review/`
> executes this; this file is the durable reference that prevents agent drift across session resets.
> Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨

## What it is

Cross-Layer Deep Audit. When `/sofi-spec-review "<feature>"` fires, the agent enters
**Lead Solution Architect + UX Principal** mode. Read-only. It inspects backend + mobile +
contract + tests as ONE interlocked block inside the unified root — no partial or surface code.

**HARD ORDERING GATE:** emit the **SEV report FIRST**. No code, no fixes, no engineering
until the 4-pillar SEV report is delivered and the 7 steel rules are verified.

## The 4-pillar matrix (mandatory scope)

### 1. 🖥️ Backend Layer (Laravel & DB)
- **DB:** unique constraints to kill Race Conditions (the karat double-index trap). Reversible migrations.
- **FormRequests & Validators:** broken requests return **422 JSON**, not **302 redirect** — protects UI toasts.
- **Security & traversal:** `/admin/*` isolation holds even under **503 maintenance**; role gate never bypassed.

### 2. 📱 Mobile & Client Layer (Flutter & Dart)
- **Exception hunting:** every network `catch (e)` → `ApiException.fromDioError(e)` → server Arabic message. No silent swallow.
- **Navigation & UI state:** login → KYC → dashboard → live ops (deposit/withdraw) — no dead route loops, no disabled buttons without clear fallback on empty data.

### 3. 🔄 API Contract & Data Sync (the bridge)
- **Contract parity:** Flutter payload ⇔ Laravel FormRequest rules, exact.
- **Physical field sync:** no scattered naming of sensitive fields — "spread/الفارق" ≠ "margin/الهامش"; verify math like `buy ≥ sell`.

### 4. 🧪 Test & Gate Readiness (ADR-004)
- Classify **Tier-A** (touches money / sensitive-data surfaces) vs **Tier-B**.
- **Tier-A ⇒ automated coverage ≥ 90% enforced immediately**; write expected Regression + Feature test structure before Gate 5.

## The 7 steel rules (non-negotiable)

| # | Rule | Pillar | Memory |
|---|------|--------|--------|
| 1 | Error → **422 JSON**, never 302 redirect (toasts render specific message) | ①/② | — |
| 2 | Every Flutter catch → `ApiException.fromDioError(e)`, no silent swallow | ③ | `sakk-mobile-dio-swallows-403` |
| 3 | `/admin/*` isolation holds even in 503 maintenance | ② | — |
| 4 | Unique DB constraint per invariant; guard double-declare migrations | ① | `migration-double-index-hazard` |
| 5 | Money math: `buy ≥ sell`, spread≠margin, true-scale, toggle keeps auto-sync | ① | `sakk-syp-magnitude-truescale`, `sakk-gold-toggle-detached-autosync` |
| 6 | API contract ⇔ Flutter payload parity; webhook shapes; no null-accessor | ①/④ | `ccpayment-deposit-webhook-shape`, `sakk-user-has-no-name-column` |
| 7 | ADR-004: Tier-A ⇒ ≥90% coverage now + written test structure | ④ | — |

## Model routing — two-phase economic grid (binding, 2026-07-01)

Ladder: 🟢 Haiku 4.5 (first line, 80% routine) → 🔵 Sonnet 5 (second line, clear-cut code) →
🔮 Fable 5 (gatekeeper) → 🟣 Opus 4.8 (last resort, 1M-ctx deep debugging — never routine code).

- **Phase 1 — scan & draft (Haiku 4.5 / Sonnet 5):** Python scanners + grep static sweep
  across folders; gather flagged files into memory; draft the raw SEV skeleton. Cheap models
  only — mechanical gathering, no judgment.
- **Phase 2 — hard gate (Fable 5):** full context handover to Fable 5 as gatekeeper — matches
  the 7 steel rules, checks Tier-A vulnerabilities, issues the FINAL SEV report and code
  approval. Fable 5 opens only for cross-layer full-stack sweeps (this gate, race conditions,
  tangled webhooks) — never for the mechanical scan.

Route map: `spec-review-scan` / `spec-review-gate` in `engine/routing/routing.yaml` (v4.2).

## Procedure (token-frugal — Python locates, model judges)

1. **Orient** — `/sofi-boot` (git sync + brain). Resolve `<FEATURE_NAME>`.
2. **Locate + scan** — `python3 engine/tooling/agents/ceo/feature_scan.py "<FEATURE>" --prj <PRJ> --md`
   then `python3 engine/tooling/agents/ceo/sofi_automator.py <project_dir>` — the 7-steel-rules scanner
   (checks: 422-JSON · Flutter swallows · admin gates · unique/race · financial logic · contracts · Tier-A coverage; `--rule N` isolates one, `--json` for machine output)
   (0 model tokens; returns file set grouped by pillar + static pre-flags). Read the skeleton, open only flagged spots.
3. **Handover** — steps 1–2 run on Haiku 4.5/Sonnet 5 (phase 1); the gathered context then
   moves whole to **Fable 5** for phase 2 (the hard gate — steps 4–5).
4. **Sweep by pillar** — confirm/rank pre-flags + semantic findings; verify all 7 steel rules; zero writes.
5. **SEV report FIRST** — 4-pillar matrix. Each finding: `SEV · file:line · defect → fix`.
   Severity 🔴 breaks/security · 🟠 correctness · 🟡 quality/taste. Normal prose, never compressed.
6. **Verdict** — per pillar (sound / at-risk / broken / **UNKNOWN**) + Tier-A/B classification + the single biggest risk. **UNKNOWN is a valid, first-class verdict** (`verification.md` V2): when the evidence can't decide a pillar, say so and route it to `sofi escalate` — never force a pass/fail. A forced binary makes an LLM-judge fabricate justification for whichever side reads more fluently.
7. **Handoff** — fixes → `/sofi-fix`; security-shaped → `/sofi-secure`; durable record → `/sofi-report audit`.

> **Judge-bias guard (v5, `verification.md` V2/V5):** Fable 5 grading work produced by other Claude-family agents carries **self-enhancement bias** (the largest, most consistent LLM-judge bias). For high-stakes / money / auth / PII verdicts, prefer a **family-diverse** judge — route the finding through the **Gemini review desk** (`external-review-desk.md`) as the second opinion rather than trusting a single same-family verdict. And periodically spot-check the trajectory behind a PASS (and any suspicious 0-finding pillar) against CEO/human review — an unaudited grader silently drifts.

## Bar
SEV report delivered before any code · all 4 pillars covered · all 7 steel rules cited pass/fail ·
every finding cites `file:line` + concrete fix · Tier-A/B classified with coverage verdict ·
per-pillar verdict · no writes, no praise, no scope creep beyond the feature.
