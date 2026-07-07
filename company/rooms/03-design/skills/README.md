# Room 03-design — Skills

> Design sits at the hinge between "what the user needs" (Research) and "what gets built" (Architecture/Build) — it wields the boot-and-close ritual skills constantly, owns `/sofi-design-taste` outright, and reaches for the heavier cross-cutting ones only when a freeze is genuinely contested. This is the room's own reading of when each `/sofi-*` skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | every `dsn-*` agent, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a screen, a token, or a string. No Design agent drafts on memory of a prior session's Journey Map. |
| `/sofi-delegate` | `dsn-lead` | Turning `res-lead`'s frozen Gate-1 bundle, or a loop-back ticket from `obs-insights-analyst`/`qa-design-auditor`, into a paste-ready four-field Work Order for the specialist who owns that piece — `dsn-ux-architect`'s flow first, always, before `dsn-ui-designer` specs a single screen. |
| `/sofi-team` | `dsn-lead` | Confirming which of the room's seven specialists (or, rarely, which agent in another room) owns a given piece of design work before drafting the Work Order — especially when a request straddles two specialties (is a "loading skeleton" a `dsn-ui-designer` state or a `dsn-motion-designer` transition?). |
| `/sofi-design-taste` | `dsn-brand-designer` (owns the dials), `dsn-a11y-specialist` (gates every proposal), `dsn-lead` (reads it at sign-off) | The room's signature skill: setting `DESIGN_VARIANCE`/`MOTION_INTENSITY`/`VISUAL_DENSITY` + a named brand preset and running the anti-generic-UI checklist — the full execution is `playbooks/anti-generic-taste-application.md`. Always paired with an a11y cross-check before anything is called final. |
| `/sofi-gate` | `dsn-lead` | The Gate-2 exit decision itself — THE FREEZE: mechanical `sofi gate-check --gate 2` plus `gtw-gatekeeper`'s fresh-context adversarial verdict — never a self-graded sign-off. This is the room's single most load-bearing skill invocation, because everything downstream inherits whatever it signs. |
| `/sofi-handoff` | every `dsn-*` agent | Closing ritual on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Runs after every specialist's draft is accepted by `dsn-lead`, and again at the room's own Gate-2 freeze. |
| `/sofi-report` | `dsn-lead` | Writing the Gate-2 accountability check-in for `brd-cpo` as a durable, evidence-backed record in the brain — especially useful when the freeze involved a contested taste-vs-a11y call that needs a citable resolution trail. |
| `/sofi-audit` (mode `ui`/`design`) | `dsn-lead` (pre-freeze pass), `dsn-brand-designer` (taste-checklist step 1) | A quick static sweep is needed before or during the Gate-2 fan-out — mostly `uiux_pipeline.py scan` and `sofi_scan.py design`, the mechanical half of both this room's playbooks. |
| `/sofi-reflect` | none directly | The room contributes signal (a repeated a11y fail, a taste dial that got reopened after a Gate-8 drop-off) but does not execute the distillation itself — that's `knw-reflector`'s job on `brd-ceo`'s schedule. Worth knowing the room's own `HANDOFFS.md` history is exactly what feeds it. |

## Rules

- `03-design` never invokes `/sofi-spec-review`, `/sofi-secure`, or `/sofi-fix` — those are Gate 3+ skills operating on code and threat surfaces this room's output hasn't reached yet. Reaching for one of them here is a sign the room has drifted past its own gate boundary.
- `/sofi-feature` is a Boardroom-commissioned, cross-gate skill; `03-design` supplies the Gate-2 slice of it when `brd-ceo` runs the full loop on a feature, but never triggers the whole arc itself.
- `/sofi-design-taste` never overrides `dsn-a11y-specialist`'s WCAG 2.2 AA matrix under any invocation — the skill's own binding rule (`.claude/skills/sofi-design-taste/SKILL.md`) and this room's `Room bar` agree completely: accessibility wins, always.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points — a genuinely contested taste-vs-a11y call or an ambiguous journey-stage-to-screen trace is exactly the kind of decision point `gtw-external-reviewer`'s desk exists for, reached through `dsn-lead`, never by a specialist directly.
