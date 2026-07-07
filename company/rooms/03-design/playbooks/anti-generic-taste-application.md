# Playbook — Anti-Generic Taste Application (specialty procedure)

> Owner: `dsn-brand-designer` (Rafael Andrade). The room's sharpest recurring job outside the core gate procedure: turning a project brief into a deliberate, defensible visual-taste decision instead of letting the product ship whatever a component library defaults to. Backs the `/sofi-design-taste` skill this room owns. Subordinate at every step to `dsn-a11y-specialist`'s WCAG 2.2 AA matrix — this playbook never produces a decision that overrides accessibility.

## When to run this

Every Gate-2 pass, once `dsn-design-system`'s base tokens and `dsn-ui-designer`'s first-pass screens exist — taste dials are applied on top of a real base, not in a vacuum before either exists. Also re-run standalone at Gate 4 when `fnt-css-artisan` needs an audit against the frozen dials, and on any Gate-8 loop-back where `obs-insights-analyst` traces a drop-off to a generic, unmemorable screen.

## Steps

### 1. Scan first — Python engine, token-frugal, 0 model tokens
```bash
python3 company/os/toolkit/uiux/uiux_pipeline.py scan --prj PRJ-XXXX [--query <screen/feature>] --md
python3 company/os/toolkit/core/sofi_scan.py design "<view/feature>" --prj PRJ-XXXX --md
```
These flag hardcoded hex values, `!important`, missing `alt`/`aria`, div-elements acting as buttons, no-reduced-motion animations, and generic-AI-UI smells (centered hero, three equal cards, one accent color, zero motion) — mechanically, before any model reads a single screen. Open only the flagged `file:line`s.

### 2. Read the inputs that actually justify a dial, not guess at them
- The project brief (business goals, target user, the emotional register the product needs to hit).
- `res-journey-architect`'s frozen emotional arc — a calm, high-stakes financial flow and a playful consumer-app flow earn different numbers on all three dials.
- `dsn-design-system`'s base tokens (the dials tune, they don't replace, the base).

### 3. Set the three dials — deliberately, one line of reasoning each
| Dial | Low (1–3) | Mid (4–6) | High (7–10) |
|------|-----------|-----------|-------------|
| `DESIGN_VARIANCE` | centered, symmetric, safe | mild asymmetry, offset grid | asymmetric / editorial / broken-grid |
| `MOTION_INTENSITY` | hover states only | entrance + scroll reveal | scroll-driven / magnetic / 3D / parallax |
| `VISUAL_DENSITY` | spacious, airy, whitespace-led | balanced | dense dashboard, tight rhythm |

Pick from the brief and the emotional arc — never from a default. Name the closest brand preset (Minimalist / Soft-Premium / Brutalist / GPT-optimized) or a documented custom blend:

| Preset | Variance | Motion | Density | Feel |
|--------|:--:|:--:|:--:|------|
| Minimalist | 2 | 2 | 3 | calm, whitespace, one accent, type-led |
| Soft / Premium | 7 | 6 | 4 | editorial, layered, tasteful motion, rich but not busy |
| Brutalist | 9 | 4 | 7 | raw grid, hard borders, mono type, high contrast |
| GPT-optimized | 4 | 3 | 5 | clean SaaS default, conversion-safe, low-risk |

### 4. Run the anti-generic-UI checklist against tokens and screens
- Every screen that defaults to centered-hero / three-equal-cards / single-accent-color without a brief-driven reason gets flagged back to `dsn-ui-designer`.
- Motion that exists only because a component library shipped it by default (not because `dsn-motion-designer` tied it to a real state change) gets flagged.
- A "premium" or "distinct" claim in the brief with no visual decision actually backing it up gets flagged as unresolved, not waved through.

### 5. Cross-check every flagged change against the a11y matrix BEFORE finalizing
```bash
sofi dispatch PRJ-XXXX --agent dsn-a11y-specialist --ticket TKT-NNN --target "taste-dial-proposals"
```
A high-`DESIGN_VARIANCE` layout that breaks focus order, a `MOTION_INTENSITY` choice with no reduced-motion fallback, or a `VISUAL_DENSITY` setting that shrinks tap targets below the WCAG 2.2 minimum are all rejected here, not shipped with a caveat. Revise the dial or the specific screen, never override the matrix.

### 6. Document the decision in the artifact
State the three final numbers, the named preset (or custom blend), and the one-line reasoning per dial directly in `docs/<PRJ>_Design_Tokens.md`'s taste section — this is what `fnt-css-artisan` audits against at Gate 4, and what `qa-design-auditor` checks built-vs-frozen fidelity against at Gate 5.

## Worked example (shape only)

```
DESIGN_VARIANCE: 6 — brief calls for "distinct, memorable" positioning against generic competitors; journey's emotional arc has a confident, exploratory peak at stage 3
MOTION_INTENSITY: 4 — entrance + scroll reveal only; stage 5 (checkout) is high-stakes and calm, no scroll-driven motion allowed there per dsn-a11y-specialist's fallback requirement
VISUAL_DENSITY: 5 — balanced; dashboard screens (stages 6-7) run denser within this budget, marketing screens (stages 1-2) run airier
Preset: Soft/Premium, custom-blended down on motion for the checkout flow
```

## Rules

- Never set a dial before `dsn-design-system`'s base tokens and `dsn-ui-designer`'s first-pass screens exist — there is nothing real to tune yet.
- Never let a dial value override `dsn-a11y-specialist`'s matrix — revise the dial or the screen, every time, no exception logged as acceptable debt.
- A dial chosen "because it looks nice" without a brief or emotional-arc citation is not accepted — `dsn-lead` rejects it back at the integration pass.
- Pairs with `/sofi-design-taste` (this whole playbook is that skill's room-level execution) and the core `gate-2-solution-design-procedure.md` (step 3 dispatches this playbook's owner).
