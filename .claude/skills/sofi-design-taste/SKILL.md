---
name: sofi-design-taste
description: Kill generic AI-UI. Set three design dials (DESIGN_VARIANCE · MOTION_INTENSITY · VISUAL_DENSITY, 1–10) + a brand preset, then apply a premium-tier taste checklist to any web/Blade/Vue view. Wielded at Gate 2 (Design) and Gate 4 (Build) by Dan (UI/UX), the frontend-react-engineer (CSS/A11y), and the backend-blade-engineer (Blade). Accessibility (WCAG 2.2 AA) always wins over any dial. Triggers — "design taste", "make it premium", "looks generic/AI", "set the dials", "brand preset", "Gate 2/4 design", "anti-generic UI".
---

# 🎨 /sofi-design-taste — anti-generic-UI dials for the SOFI frontend squad

Generic AI UI = centered hero, three equal cards, one accent color, no motion, no opinion.
This skill forces a **taste decision** before styling: three dials + a brand preset, applied 1:1
to the frozen prototype (`[ID]_Prototype_Spec.md`) and content strings (`[ID]_Content_Strings.json`).

> **Hard rule — a11y always wins.** No dial setting overrides WCAG 2.2 AA. The
> frontend-react-engineer (`sofi-frontend-react-engineer`) gates contrast, focus order, motion-reduce, target size.
> `MOTION_INTENSITY` respects `prefers-reduced-motion`. Taste never ships an inaccessible view.

Source power: `taste-skill` (`engine/SUPERPOWERS.md` §3). SOFI-native — no external dependency.

---

## 0. Scan first (Python engine — token-frugal, 0 model tokens)

```bash
python3 engine/tooling/agents/ceo/sofi_scan.py design "<view/feature>" --prj <PRJ> --md   # hardcoded hex, px, !important, missing alt/aria, div-buttons, no reduced-motion, RTL, AI-UI smells
python3 engine/tooling/agents/ceo/sofi_scan.py flow "" --prj <PRJ> --md                    # routes → views map + orphan/dead-end views (UserFlow / UX journey gaps)
```
Read the skeleton; open only flagged `file:line`. Then set the dials below and apply the taste checklist to what the scan surfaced.

## 1. The three dials (1–10)

| Dial | Low (1–3) | Mid (4–6) | High (7–10) |
|------|-----------|-----------|-------------|
| `DESIGN_VARIANCE` | centered, symmetric, safe | mild asymmetry, offset grid | asymmetric / editorial / broken-grid |
| `MOTION_INTENSITY` | hover states only | entrance + scroll reveal | scroll-driven / magnetic / 3D / parallax |
| `VISUAL_DENSITY` | spacious, airy, whitespace-led | balanced | dense dashboard, tight rhythm |

Pick each dial **from the project brief**, not by default. State the three numbers in the
Gate-2 handoff so Gate-4 build can audit against them.

## 2. Brand presets (starting points — tune per brief)

| Preset | Variance | Motion | Density | Feel |
|--------|:--:|:--:|:--:|------|
| **Minimalist** | 2 | 2 | 3 | calm, whitespace, one accent, type-led |
| **Soft / Premium** | 7 | 6 | 4 | editorial, layered, tasteful motion, rich but not busy |
| **Brutalist** | 9 | 4 | 7 | raw grid, hard borders, mono type, high contrast |
| **GPT-optimized** | 4 | 3 | 5 | clean SaaS default, conversion-safe, low-risk |

Default for a **premium brand** = Soft/Premium (**variance 7 · motion 6 · density 4**).

## 3. Apply — Gate 2 (Design) → Gate 4 (Build)

**Gate 2 (Dan + the frontend-react-engineer):** choose preset → set the 3 dials → record them on the prototype spec.
Each dial choice must trace to a journey stage / brand attribute (Design is Truth).

**Gate 4 (backend-blade-engineer + frontend-react-engineer):** build to the dials, then run the audit below before PR.

## 4. Gate-4 taste audit checklist (built view vs the dials)

- [ ] **Not-generic:** layout is not centered-hero + 3 equal cards unless variance ≤3 was chosen on purpose.
- [ ] **Variance honored:** asymmetry / editorial rhythm present iff `DESIGN_VARIANCE ≥7`.
- [ ] **Motion honored:** scroll/magnetic/3D present iff `MOTION_INTENSITY ≥7`; **all** motion behind `prefers-reduced-motion: reduce`.
- [ ] **Density honored:** spacing rhythm matches `VISUAL_DENSITY` (airy vs tight), consistent scale (4/8px).
- [ ] **Type has a point of view:** ≥2 weights, deliberate scale ramp — not a single system-font size.
- [ ] **Color is opinionated:** brand accent + supporting tones, not one flat primary on white.
- [ ] **State coverage:** empty · loading · error states are designed, not afterthoughts.
- [ ] **A11y (Grace gates, non-negotiable):** contrast ≥4.5:1 body / 3:1 large, visible focus ring, logical tab order, ≥24px targets, motion-reduce respected. **Fails here = view rejected regardless of taste.**

## 5. Output

Return, in one block: chosen preset · the 3 dial values · one-line rationale per dial (traced to
journey/brand) · the audit result (pass / rejected-with-reasons). Hand to Théo for the Gate-4 PR.
