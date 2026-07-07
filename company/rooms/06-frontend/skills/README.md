# Room 06-frontend — Skills

> Frontend sits at the hinge between the frozen contract and the screen a real hand touches — it wields the boot-and-close ritual skills every Gate-4 pass, plus `/sofi-design-taste` as the working reference `fnt-css-artisan` applies against the token file. This is the room's own reading of when each `/sofi-*` skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | every `fnt-*` agent, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a frozen contract. No Frontend agent builds a component on memory. |
| `/sofi-delegate` | `fnt-lead` | Turning the Gate-3 freeze into a paste-ready four-field Work Order for the specialist who owns the next piece — the framework engineer (`fnt-vue-engineer` or `fnt-react-engineer`, matching `Tech_Stack.md`) first, always, before styling/motion/hardening fan out behind the component skeleton. |
| `/sofi-team` | `fnt-lead` | Confirming which of the room's seven specialists (or, rarely, which squad-partner agent in `05-backend`/`07-mobile`) owns a given piece of Gate-4 work before drafting the Work Order — especially when a finding straddles two specialists (a reduced-motion fallback touching both `fnt-interaction-engineer` and `fnt-a11y-engineer`). |
| `/sofi-gate` | `fnt-lead` | This room's slice of the Gate-4 merge decision: mechanical `sofi gate-check --gate 4 --room 06-frontend` plus `fnt-code-reviewer`'s fresh-context adversarial verdict — never a self-graded merge. Wraps steps 10-11 of `playbooks/gate-4-frontend-build.md`. |
| `/sofi-handoff` | every `fnt-*` agent | Closing ritual on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Runs after every specialist's draft is accepted by `fnt-lead`, and again at this room's own Gate-4 close. |
| `/sofi-design-taste` | `fnt-css-artisan` (applies, doesn't set) | Consulted while applying `Design_Tokens.md`'s taste dials and the anti-generic-UI checklist in code — the dials and brand preset themselves are `03-design`'s (`dsn-brand-designer`'s) artifact; this room reads and applies them, never redefines them. |
| `/sofi-report` | `fnt-lead` | Writing this room's Gate-4 status check-in for `brd-ceo`/`brd-cto`/`bck-lead` as a durable, evidence-backed record rather than letting a merge summary live only in chat. |
| `/sofi-fix` | `fnt-lead` (receives, routes) | The landing point for a `qa-design-auditor` or `qa-perf-analyst` finding routed back from Gate 5 — `fnt-lead` routes the repair to the owning specialist and re-runs `playbooks/a11y-performance-hardening.md` on the fix. |
| `/sofi-spec-review` | none directly (this room's diffs are a common *subject* of it, never the invoker) | `arc-review-architect` may address `fnt-lead` for the frontend slice of a cross-layer feature review; this room supplies evidence, doesn't run the review itself. |
| `/sofi-secure` | none directly (routed) | A security-shaped finding in a frontend diff (e.g. a token stored insecurely client-side) routes to `09-security` via `fnt-lead`; `06-frontend` flags, `09-security` (through `sec-lead`) owns the security response. |
| `/sofi-reflect` | none directly | The room contributes signal (a Gate-4 rejection, a recurring `store-with-two-owners`-shaped finding, a repeated reduced-motion regression) but does not execute the distillation itself — that's `knw-reflector`'s job on `brd-ceo`'s schedule. Worth knowing this room's own `HANDOFFS.md` history, and every hardening-pass finding, are exactly what feeds it. |

## Rules

- `06-frontend` never invokes `/sofi-feature` itself — that is a Boardroom-commissioned, cross-gate skill; this room supplies its Gate-4 slice when `brd-ceo` runs the full loop, but never triggers the whole arc.
- `fnt-code-reviewer` never runs `/sofi-audit` — a per-layer sweep is a different, broader instrument than the fixed-scope fresh-context diff review (V2) this room's reviewer performs on one merge at a time; conflating the two is a category error this room's members are trained to catch.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points — an `UNKNOWN` verdict from `fnt-code-reviewer` on a diff touching money, auth, or PII fields is exactly the kind of decision point `gtw-external-reviewer`'s desk exists for, reached through `fnt-lead`, never by a specialist mid-diff.
