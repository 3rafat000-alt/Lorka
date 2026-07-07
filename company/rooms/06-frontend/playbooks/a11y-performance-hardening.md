# Playbook — A11y + Performance Hardening

> Owner: `fnt-lead` (running: `fnt-a11y-engineer`, `fnt-performance-engineer`). The room's sharpest recurring specialty — the pre-merge hardening pass every component diff runs through before it ever reaches `fnt-code-reviewer`. Closes the gap between "looks done" (passed the design-phase matrix, felt fast in the browser) and "is done" (verified against the live DOM, measured against a recorded baseline).

## When to run this

Every component diff, every time, between step 6 and step 7 of `playbooks/gate-4-frontend-build.md` — never skipped for a "small" change, because a small change is exactly the kind that regresses a baseline nobody re-checks. Also re-run standalone whenever `10-quality`'s `qa-design-auditor` or `qa-perf-analyst` reports a Gate-5 fidelity or performance finding that traces back to this room.

## Steps

### 1. Orient on what changed
```bash
git -C projects/PRJ-XXXX diff --stat wt/PRJ-XXXX-gate4-frontend
```
Read the diff's file list before opening anything — know which components, stores, and styles actually changed versus what's unrelated noise in the worktree.

### 2. `fnt-a11y-engineer` — keyboard-only pass, first, before anything else
Tab through every interactive flow the diff touches, keyboard only:
- Reachability: can every control be reached without a mouse?
- Visible focus: is the focus indicator visible at every stop, not suppressed with no replacement?
- Logical order: does tab order match the visual/reading order, not the DOM's incidental structure?

### 3. `fnt-a11y-engineer` — ARIA and narration check
For every interactive or dynamic region: does the ARIA role/label/live-region actually narrate correctly, not merely exist? A duplicated or contradictory `aria-label`, or a live region that never fires, is a fail even though the attribute is present in the markup.

### 4. `fnt-a11y-engineer` — contrast, target size, reduced-motion cross-check
```bash
# project's contrast/lint tooling, e.g.:
npx axe-core <url-or-component> --tags wcag22aa
```
Cross-check `fnt-css-artisan`'s rendered contrast and tap-target sizes against WCAG 2.2 AA thresholds; confirm `fnt-interaction-engineer`'s `prefers-reduced-motion` media query actually fires and the fallback preserves the original information (not a bare `animation: none`).

### 5. `fnt-a11y-engineer` writes the audit
```bash
sofi checkpoint PRJ-XXXX "wip(frontend): a11y audit pass — <component/flow>"
```
Update `docs/PRJ-XXXX_Frontend_A11y_Audit.md`: one row per component/criterion, pass/fail cited to the exact WCAG 2.2 AA success criterion, the fix named if failing. Any fail routes back to the owning specialist (`fnt-vue-engineer`/`fnt-react-engineer`/`fnt-css-artisan`/`fnt-interaction-engineer`) through `fnt-lead` — never fixed by `fnt-a11y-engineer` directly.

### 6. `fnt-performance-engineer` — record the pre-diff baseline (if not already on file)
```bash
python3 company/os/agents/tier-3-quality/performance-load-analyst/perf_budget.py projects/PRJ-XXXX/_scratch/baseline-metrics.json
```
If a baseline for this route doesn't already exist in `docs/PRJ-XXXX_Frontend_Perf_Baseline.md`, measure it now, before evaluating the diff — a regression is invisible without a "before" number.

### 7. `fnt-performance-engineer` — measure the diff
```bash
# project's build + Lighthouse/CWV tooling, e.g.:
npm run build -- --analyze
npx lighthouse <url> --output=json --output-path=projects/PRJ-XXXX/_scratch/post-diff.json
python3 company/os/agents/tier-3-quality/performance-load-analyst/perf_budget.py projects/PRJ-XXXX/_scratch/post-diff.json
```
Check bundle-analyzer output for an oversized dependency or an unsplit chunk; check `perf_budget.py`'s exit code — `0` within budget, `1` breached.

### 8. `fnt-performance-engineer` writes the baseline update
Update `docs/PRJ-XXXX_Frontend_Perf_Baseline.md` with the before/after LCP/INP/CLS and bundle-size numbers per affected route. A breach or a regression routes back to the owning specialist through `fnt-lead`, with the exact numbers named — never a qualitative "feels slower."

### 9. `fnt-lead` confirms both are clean before advancing
No diff proceeds to `fnt-code-reviewer` (step 7 of the core playbook) while either `docs/PRJ-XXXX_Frontend_A11y_Audit.md` or `docs/PRJ-XXXX_Frontend_Perf_Baseline.md` carries an open finding for the components in this diff.

## Self-check before advancing to review

1. Was the keyboard-only pass run on every new or changed interactive element?
2. Does every ARIA attribute narrate correctly, not just exist in the markup?
3. Is the reduced-motion fallback confirmed firing, not just coded?
4. Is there a recorded pre-diff baseline this measurement compares against?
5. Are LCP, INP, CLS, and bundle size all within budget — checked individually, never a single averaged score?

## Rules

- This pass runs on every diff, no exceptions for "small" changes — small changes are exactly where a regression hides longest.
- Neither `fnt-a11y-engineer` nor `fnt-performance-engineer` fixes what they find — findings route back to the owning specialist through `fnt-lead`, diagnosis and repair stay separate roles.
- `perf_budget.py` is owned by `10-quality`'s `qa-perf-analyst` and enforced for real at Gate 5 — this room runs it pre-emptively to avoid a Gate-5 bounce-back, never as a substitute for the formal Gate-5 pass.
- Pairs with `playbooks/gate-4-frontend-build.md` (steps 6-7) and `/sofi-fix` when a Gate-5 finding sends work back into this room.
