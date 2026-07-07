---
name: sofi-spec-review
description: Cross-layer feature review as arc-review-architect — inspect one feature through a fixed 4-pillar matrix (Data & Logic · Admin & Ops · UI/UX & Taste · Edge Cases & Gaps), read-only, cite file:line, rank by severity, enforce the 7 steel rules. Deeper and more opinionated than /sofi-audit's per-layer sweep; use when one whole feature needs an architect's verdict. Triggers — "spec review", "review the <feature> feature", "architect review", "4-pillar review", "is this feature sound", "full review of payments/auth/kyc".
---

# /sofi-spec-review — one feature, four pillars, an architect's verdict

> Deeper than `/sofi-audit` (which sweeps one *layer*). This reviews one *feature*
> end-to-end as the Lead Solution Architect + UX Principal would. Owner: **`arc-review-architect`**
> (Architecture room). **Read-only. Never writes.** Playbook: `company/rooms/04-architecture/playbooks/spec-review.md`.

**Usage:** `/sofi-spec-review "<feature>"` — e.g. `"نظام المدفوعات"`, `"KYC"`, `"payroll"`.

## Injected directive (act on this exactly)

```
[SOFI SYSTEM PROMPT]
Act as arc-review-architect — Lead Solution Architect & UX Principal. Inspect the feature
<FEATURE_NAME> across all layers. Do NOT write code (Read-only static sweep).
Evaluate and output the results using the following 4-pillar matrix:

1. Data & Logic Layer: DB schema soundness, N+1 query risks, and backend API shapes.
2. Admin & Ops Control: Dashboard visibility, audit logs, and status state-machine logic.
3. UI/UX & Taste: Application views evaluated by DESIGN_VARIANCE, MOTION, DENSITY, and WCAG AA accessibility.
4. Edge Cases & Gaps: Where does the business logic break? (e.g., interrupted payments, null-pointer shapes).

Cite file:line for every finding and rank by severity (🔴🟠🟡). Use normal prose (never compressed).

HARD GATE — emit the SEV report FIRST. No code, no fixes, no engineering until
the 4-pillar SEV report is delivered. "Design is Truth · big brain small mouth."
```

## The 7 steel rules (non-negotiable — verify every one, every review)

Every spec-review MUST check these seven. A pillar is NOT "sound" until its rules pass.

1. **422-JSON on error, never 302 redirect** — broken/validation requests return `422` JSON
   (not a `302` redirect) so UI toasts render the specific message. Grep FormRequests +
   controller catch blocks + `expectsJson`. (Pillar ①/②)
2. **`ApiException.fromDioError(e)` in every Flutter catch** — no silent swallow, no raw
   `"خطأ تقني 403"`. Every `catch (e)` on a network call maps to the server's Arabic message.
   [[sakk-mobile-dio-swallows-403]]. (Pillar ③)
3. **`/admin/*` isolation holds even in 503 maintenance** — admin auth + role gate never
   bypassed while the app serves maintenance. Verify middleware order. (Pillar ②)
4. **Unique constraints against race conditions** — every "one per X" invariant is a DB
   `unique` index, not app-only. Guard follow-up migrations against double-declare
   [[migration-double-index-hazard]]. Watch the karat-index trap. (Pillar ①)
5. **Money math correct & fields un-scattered** — `buy ≥ sell` enforced; "spread/الفارق"
   kept distinct from "margin/الهامش"; true-scale honored [[sakk-syp-magnitude-truescale]];
   toggle never detaches auto-sync [[sakk-gold-toggle-detached-autosync]]. (Pillar ①)
6. **API contract ⇔ Flutter payload parity** — the payload Flutter sends matches the Laravel
   FormRequest rules exactly; webhook shapes verified [[ccpayment-deposit-webhook-shape]];
   no null-accessor traps [[sakk-user-has-no-name-column]]. (Pillar ①/④)
7. **ADR-004 Gate-5 coverage** — classify the feature Tier-A (touches money/sensitive-data
   surfaces) or Tier-B. **Tier-A ⇒ automated coverage ≥ 90% enforced immediately**; write the
   expected Regression + Feature test structure before it can pass Gate 5. (Pillar ④)

## Model routing — two-phase economic grid (binding · `company/nexus/routing.yaml`)

- **Phase 1 — scan & draft (🟢 mechanical `haiku` / 🔵 workhorse `sonnet`):** run the Python scanners
  (0 model tokens), grep static sweep across folders, gather flagged files into memory, and draft the
  raw SEV skeleton. Cheap models only — no judgment calls here.
- **Phase 2 — hard gate (🔮 gatekeeper tier · session model):** hand the ENTIRE gathered context to the
  gatekeeper-tier model. It matches the 7 steel rules, checks Tier-A vulnerabilities, issues the final
  SEV report, and grants/denies code approval. The gatekeeper tier is opened ONLY for this cross-layer
  gate — never for the mechanical scan. Deep `opus` stays out entirely (last-resort debugging only).
  Route map: `spec-review-scan` / `spec-review-gate` in `company/nexus/routing.yaml`.

## Procedure

1. **Orient** — `/sofi-boot` (git sync + brain). Resolve `<FEATURE_NAME>` from the arg.
2. **Locate + steel-rule scan — Python tools (token-frugal, 0 model tokens):**
   ```bash
   python3 company/os/agents/ceo/feature_scan.py "<FEATURE_NAME>" --prj <PRJ> --md
   python3 company/os/agents/ceo/sofi_automator.py <project_dir>          # 7-steel-rules scanner (--rule N to isolate)
   python3 company/os/agents/ceo/spec_review_preflight.py "<FEATURE_NAME>" --prj <PRJ>   # gathers Phase-1 context bundle
   ```
   `feature_scan` returns the file set grouped by the 4 pillars + static pre-flags;
   `sofi_automator` runs all 7 steel rules and emits the raw 🔴/🟡 SEV skeleton.
   **Read these skeletons instead of the tree.** Open only flagged spots; confirm/refute each flag.
3. **Sweep by pillar** (confirm/rank the pre-flags + add semantic findings; zero writes) — apply the injected matrix:
   - **① Data & Logic** — schema/indexes, `->with` gaps (N+1), migration rollback, `$fillable`/`$guarded` traps ([[guarded-field-mass-assignment-bug]]), API/webhook shape ([[ccpayment-deposit-webhook-shape]]), true-scale ([[sakk-syp-magnitude-truescale]]).
   - **② Admin & Ops** — admin dashboard visibility, audit logs, status state-machine correctness (illegal transitions, stuck states).
   - **③ UI/UX & Taste** — views vs the 3 dials (DESIGN_VARIANCE·MOTION·DENSITY) + WCAG 2.2 AA; run `/sofi-design-taste` for depth; RTL/`&lrm;`, swallowed errors ([[sakk-mobile-dio-swallows-403]]), null accessors ([[sakk-user-has-no-name-column]]).
   - **④ Edge Cases & Gaps** — where logic breaks: interrupted/partial payments, double-submit, offline, null shapes, race on shared state, empty/huge input, locale.
4. **Output** — the 4-pillar matrix. Each finding: `SEV · file:line · defect → fix`. Severity 🔴 breaks/security · 🟠 correctness · 🟡 quality/taste. **Normal prose, never compressed** (Article 05).
5. **Verdict** — per pillar: sound / at-risk / broken, one line each. Then the single biggest risk.
6. **Oracle desk (standing, before handoff)** — push the SEV verdict through the desk:
   `sofi oracle review --prj <PRJ> --json --text "<the 4-pillar findings + context + ask for detailed remediation guidance>"`
   (inline, never a `.md`). Then ANALYZE + EXECUTE the reply autonomously and loop till the feature
   converges — don't stop to ask (Teaching VII; operator `gtw-external-reviewer`;
   `company/os/oracle/GEMINI_LOOP_ARCHITECTURE.md`).
7. **Handoff** — fixes → `/sofi-fix "<feature>"`; security-shaped → `/sofi-secure`; durable record → `/sofi-report audit`.

**Bar:** SEV report delivered BEFORE any code; all 4 pillars covered; all 7 steel rules verified
(each pass/fail cited); every finding cites `file:line` + concrete fix; Tier-A/B classified with
the ≥90% coverage verdict; ends with a per-pillar verdict. No writes, no praise, no scope creep.
Verification law: `company/constitution/03-verification.md`. Playbook: `company/rooms/04-architecture/playbooks/spec-review.md`.
