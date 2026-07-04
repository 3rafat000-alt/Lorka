---
name: sofi-feature
description: The one big command — take a feature end-to-end through the full SOFI loop in a single invocation: static Python scan (token-frugal) → 4-pillar architect review → route fixes to specialist agents → verify → report → gate → handoff. Cheapest cost, highest effort: Python does the heavy locating/pre-flagging so the model spends tokens only on judgment. Use to inspect AND repair a whole feature. Triggers — "work the whole <feature>", "full pass on payments", "review and fix the feature", "do everything for <feature>", "end-to-end <feature>".
---

# /sofi-feature — one command, whole feature, full loop

> **Cheapest cost, highest effort.** A Python tool does the deterministic heavy lifting
> (locate files, bucket by pillar, pre-flag suspects) with **zero model tokens**. The
> model reads one compact JSON and spends its tokens only on judgment + fixes.
> Doctrine: *few token do trick* · CEO no-write ([[ceo-orchestrator-no-write-doctrine]]).

**Usage:** `/sofi-feature "<feature>" [PRJ-ID]` — e.g. `"نظام المدفوعات"`, `"KYC"`.

## Pipeline (each step feeds the next)

### 0. Orient
`/sofi-boot` — git sync + brain. Resolve `<feature>` + PRJ.

### 1. Scan (Python, token-frugal — the token saver)
```bash
python3 engine/tooling/agents/ceo/feature_scan.py "<feature>" --prj <PRJ> --md         # 4-pillar file-set + pre-flags
python3 engine/tooling/agents/ceo/sofi_scan.py security "<feature>" --prj <PRJ> --md    # OWASP pre-flags
python3 engine/tooling/agents/ceo/sofi_scan.py design   "<feature>" --prj <PRJ> --md    # taste/a11y/RTL pre-flags
python3 engine/tooling/agents/ceo/sofi_scan.py wiring   "<feature>" --prj <PRJ> --md    # interconnection gaps
python3 engine/tooling/agents/ceo/sofi_scan.py flow      ""         --prj <PRJ> --md    # UserFlow + orphan views
```
Emits compact skeletons: file set by pillar + static pre-flags across data, security,
design, wiring, and UserFlow (`file:line · hint · severity`). **Read these instead of
the source tree.** JSON mode (drop `--md`) when you want to program over them.

### 2. Review (model judgment — /sofi-spec-review matrix)
For each pre-flag, open **only** that `file:line`, confirm or dismiss, rank
🔴🟠🟡. Add semantic findings the heuristics can't see (business logic, state
machines, taste, a11y). Output the 4-pillar matrix. Pull in `/sofi-design-taste`
for pillar ③ depth, `/sofi-secure` if a 🔴 is security-shaped. Normal prose.

### 3. Fix (specialist agents write, CEO routes)
`/sofi-fix "<feature>"` — group confirmed findings by owning agent
(blade/controller→`sofi-backend-blade-engineer`,
schema→`sofi-data-schema-engineer`, css→`sofi-frontend-react-engineer`, …),
build each RCCF via `/sofi-delegate`, spawn independent groups in parallel,
**checkpoint each change**. I never author code.

### 4. Verify
Security fixes → `/sofi-secure verify`. Tests → run suite. UI → `view:cache`
compiles. Re-run step 1 scan to confirm pre-flags cleared.

### 5. Report → Review desk → Gate → Handoff
`/sofi-report audit` (durable, EN/AR, commit-traced) →
**review desk (standing):** `sofi gemini review --prj <PRJ> --json --text "<verdict + context + ask>"` (inline) → analyze + EXECUTE the reply, loop till done, don't ask (`engine/protocols/external-review-desk.md`) →
`/sofi-gate` (bar met? advance one) →
`/sofi-handoff` (head_sha + next ticket).

## Why it's cheap
- Locating + pre-flagging = **Python, 0 tokens**. Model would burn thousands reading dozens of files.
- Model opens only flagged `file:line` spots, not whole files → ~70–90% fewer read tokens.
- Static grep first, agents only to fix, opus only for security/API/arbitration.

## Bar
All 4 pillars covered · every finding cites `file:line` + concrete fix · every fix committed or explicitly deferred with reason · report written · gate decision made. No writes outside step 3's delegated agents. No scope creep beyond the feature.
