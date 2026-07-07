# Playbook — Spec Review (Cross-Layer Deep Audit)

> Owner: `arc-review-architect` (Dr. Mei-Ling Fong). Read-only, cross-gate. The room's sharpest recurring specialty job and the binding procedure behind `/sofi-spec-review "<feature>"` (`.claude/skills/sofi-spec-review/SKILL.md`). Not sequenced inside Gate 3 — reachable by any room's Lead at any gate a feature needs a full cross-layer verdict, most commonly just before or during Gate 4/5 once a feature's build is far enough along to inspect end-to-end.

## When to run this

Whenever any room's Lead needs a whole-feature verdict across every layer at once — before a risky Gate-5 pass, when a race condition or a tangled webhook is suspected, when "is this feature sound" genuinely needs an architect's answer rather than a single specialist's opinion, or as the deeper follow-up to a `/sofi-audit` finding that turned out to be feature-shaped rather than layer-shaped.

## Steps

### 1. Orient and resolve the feature
```bash
sofi sync PRJ-XXXX
```
`/sofi-boot` first — git sync + brain, never a review on memory. Resolve `<FEATURE_NAME>` exactly as named in the request; never widen or narrow the scope on your own initiative. If the request is genuinely ambiguous about which feature is meant, ask the requesting Lead before scanning anything.

### 2. Locate + steel-rule scan — Python tools, zero model tokens
```bash
python3 company/os/toolkit/ceo/feature_scan.py "<FEATURE_NAME>" --prj PRJ-XXXX --md
python3 company/os/toolkit/ceo/sofi_automator.py projects/PRJ-XXXX          # 7-steel-rules scanner; --rule N isolates one, --json for machine output
python3 company/os/toolkit/ceo/spec_review_preflight.py "<FEATURE_NAME>" --prj PRJ-XXXX  # Phase-1 context bundle
```
`feature_scan.py` returns the file set grouped by the 4 pillars plus static pre-flags. `sofi_automator.py` runs all 7 steel rules and emits the raw 🔴/🟡 SEV skeleton. **Read these skeletons instead of the tree.** Open only flagged spots; confirm or refute each flag yourself — the scanners locate, the model judges.

### 3. Two-phase economic handover
Steps 1–2 run on mechanical/workhorse tier (`spec-review-scan` route, `company/nexus/routing.yaml`) — pure gathering, no judgment. The gathered context then moves whole to `arc-review-architect` at gatekeeper tier (`spec-review-gate` route) for the hard gate below. The gatekeeper tier opens only for this cross-layer sweep — never for the mechanical scan itself, and deep `opus` tier stays out entirely (last-resort debugging only, never routine review).

### 4. Sweep by pillar — the fixed 4-pillar matrix (never skip one)
Confirm/rank the pre-flags and add semantic findings; zero writes throughout.

- **① Data & Logic** — schema/index soundness, N+1 query risk (missing eager-load), migration rollback presence, mass-assignment traps, API/webhook shape correctness, money-math scale correctness where the feature touches financial values.
- **② Admin & Ops Control** — admin/dashboard visibility, audit-log completeness, status state-machine correctness (illegal transitions, stuck states), authorization isolation holding even under maintenance/degraded modes.
- **③ UI/UX & Taste** — the feature's views against the three taste dials (`DESIGN_VARIANCE`/`MOTION_INTENSITY`/`VISUAL_DENSITY`) and WCAG 2.2 AA (`/sofi-design-taste` for depth); every client-side error path resolves to a specific, actionable message — never a swallowed or generic failure.
- **④ Edge Cases & Gaps** — where the business logic actually breaks: interrupted/partial transactions, double-submit, offline/degraded network, null/empty shapes, race conditions on shared state, locale and empty/huge-input handling.

### 5. Verify the 7 steel rules (every review, every time — never assumed clean)
1. Error responses return a structured `422`-class body, never a bare redirect — the client's error surface renders the specific message.
2. Every client-side network exception maps to a typed exception carrying the server's real message — no silent swallow, no generic fallback string.
3. Admin/privileged surfaces stay isolated even under maintenance or degraded modes — the role gate is never bypassed.
4. Every "one per X" invariant is backed by a real unique database constraint, not app-only logic; migrations guard against double-declaring the same index.
5. Money math is internally consistent (a buy price never crosses a sell price the wrong direction, distinct fields stay distinct, scale/precision is honored end to end) wherever the feature touches financial values.
6. The client payload and the server contract match exactly — no field drift, no null-accessor trap, webhook shapes verified against source.
7. The feature is classified Tier-A (touches money/sensitive-data surfaces) or Tier-B; Tier-A demands ≥90% automated coverage enforced now, with the expected test structure named even if not yet written.

### 6. Output — the SEV report FIRST (the hard ordering gate)
No code, no fix, no engineering discussion until this report ships. Each finding: `SEV · file:line · defect → fix`. Severity 🔴 breaks/security · 🟠 correctness · 🟡 quality/taste. **Normal prose, never compressed** — `caveman: off` is not a default for this role, it is a hard mode.

### 7. Verdict — per pillar, including UNKNOWN
One line per pillar: sound / at-risk / broken / **UNKNOWN**. Then the single biggest risk across the whole feature. `UNKNOWN` is a valid, first-class verdict (`company/constitution/03-verification.md`, V2) — when the evidence genuinely can't decide a pillar, say so and route it to `sofi escalate`; never force a binary. A forced binary makes an LLM-judge fabricate justification for whichever side reads more fluently.

### 8. Judge-bias guard (money/auth/PII findings)
Grading work produced by other Claude-family agents carries self-enhancement bias — the largest, most consistent LLM-judge bias. For high-stakes verdicts, name the recommendation to route the finding through the Gemini review desk (`gtw-external-reviewer`, `company/os/oracle/`) as a family-diverse second opinion rather than trusting a single same-family verdict standing alone. Periodically, a fresh pair of eyes should spot-check the trajectory behind a PASS (and any suspicious 0-finding pillar) — an unaudited grader drifts silently.

### 9. Handoff
The requesting room's Lead receives the SEV report and routes it onward: fixes → `/sofi-fix "<feature>"`; security-shaped findings → `/sofi-secure`; a durable record → `/sofi-report audit`. `arc-review-architect` never performs any of these three itself.

## Worked shape (what the SEV report looks like)

```
## Spec Review — <FEATURE_NAME> (PRJ-XXXX)

### ① Data & Logic
🔴 file.php:42 — missing unique constraint on <column>, allows a race-condition duplicate → add a DB-level unique index + migration with tested rollback.
...verdict: at-risk

### ② Admin & Ops
...verdict: sound

### ③ UI/UX & Taste
...verdict: UNKNOWN — insufficient evidence to judge the empty-state screen; escalating.

### ④ Edge Cases & Gaps
...verdict: broken

### 7 Steel Rules
1. PASS  2. PASS  3. PASS  4. FAIL (see ①)  5. N/A  6. PASS  7. Tier-A, coverage 62% — FAIL

### Biggest risk
<one line>
```

## Rules

- Read-only, always — `arc-review-architect` holds no `Write`/`Edit` tool and never will; a "review" that also patches the code has stopped being a review.
- Never skip a pillar because the feature "obviously" doesn't touch it — that assumption is exactly where findings hide.
- Never default an undecidable pillar to PASS — `UNKNOWN` ships, cited, and escalates.
- Pairs with `/sofi-spec-review` (the skill wrapping this whole procedure) and `playbooks/gate-3-architecture.md` (the room's other core procedure — this one is deliberately not part of that sequence).
