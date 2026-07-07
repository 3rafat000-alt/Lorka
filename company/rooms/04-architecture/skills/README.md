# Room 04-architecture — Skills

> Architecture sits at the hinge between design prose and code — it wields the boot-and-close ritual skills every Gate-3 pass, and it is the sole owner of the one skill that reaches across every gate after it: `/sofi-spec-review`. This is the room's own reading of when each `/sofi-*` skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | every `arc-*` agent, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a frozen prototype. No Architecture agent drafts a stack, schema, or contract on memory. |
| `/sofi-delegate` | `arc-lead` | Turning the Gate-2 freeze into a paste-ready four-field Work Order for the specialist who owns the next piece — `arc-system-architect` first, always, before schema/contract/integrations fan out behind the stack. |
| `/sofi-team` | `arc-lead` | Confirming which of the room's six specialists (or, rarely, which squad-partner agent in `08-data`/`09-security`) owns a given piece of Gate-3 work before drafting the Work Order — especially when a finding straddles two specialists (a webhook shape touching both `arc-api-architect` and `arc-integration-architect`). |
| `/sofi-gate` | `arc-lead` | The Gate-3 exit decision itself: mechanical `sofi gate-check --gate 3` plus `gtw-gatekeeper`'s fresh-context adversarial verdict — never a self-graded sign-off. The room's single most load-bearing skill invocation, wrapping steps 10-11 of `playbooks/gate-3-architecture.md`. |
| `/sofi-handoff` | every `arc-*` agent | Closing ritual on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Runs after every specialist's draft is accepted by `arc-lead`, and again at the room's own Gate-3 close. |
| `/sofi-spec-review` | `arc-review-architect` (owner) | The room's standing, cross-gate specialty: a fixed 4-pillar cross-layer review of one feature plus the 7 steel rules, SEV report first, read-only. Reachable by any room's Lead at any gate — most often invoked just before or during Gate 4/5 once a feature is far enough along to inspect end-to-end. Binding procedure: `playbooks/spec-review.md`. |
| `/sofi-report` | `arc-lead`, `arc-review-architect` | Writing the Gate-3 accountability check-in for `brd-ceo`/`brd-cto` as a durable, evidence-backed record, and writing a spec-review's findings up for the brain (`/sofi-report audit`) rather than letting a SEV report live only in chat. |
| `/sofi-fix` | none directly (routed, never executed here) | `arc-review-architect` never runs `/sofi-fix` itself — it hands the SEV report to the requesting room's Lead, who routes remediation to the owning specialist. Worth knowing this room's boundary: diagnosis here, repair elsewhere, always. |
| `/sofi-secure` | none directly (routed) | Security-shaped spec-review findings route to `09-security` via the requesting Lead — `04-architecture` flags, `09-security` (through `sec-lead`) owns the security response. |
| `/sofi-design-taste` | `arc-review-architect` (reference only, during pillar ③) | Consulted for depth on the UI/UX & Taste pillar of a spec review — the taste dials and WCAG matrix themselves are `03-design`'s artifact; this room reads them, never redefines them. |
| `/sofi-reflect` | none directly | The room contributes signal (a Gate-3 rejection, a recurring `migration-double-index-hazard`-shaped finding) but does not execute the distillation itself — that's `knw-reflector`'s job on `brd-ceo`'s schedule. Worth knowing the room's own `HANDOFFS.md` history, and every spec-review's findings, are exactly what feeds it. |

## Rules

- `04-architecture` never invokes `/sofi-feature` itself — that is a Boardroom-commissioned, cross-gate skill; this room supplies its Gate-3 slice when `brd-ceo` runs the full loop, but never triggers the whole arc.
- `arc-review-architect` never invokes `/sofi-audit` — that is a per-layer sweep owned by whichever room's Lead requests it; `/sofi-spec-review` is deliberately the deeper, feature-scoped, architect-owned alternative, and conflating the two is a category error this room's members are trained to catch.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points — a contested stack call, an `UNKNOWN` pillar verdict on a money/auth/PII feature, or a thin `Integration_Plans.md` citation is exactly the kind of decision point `gtw-external-reviewer`'s desk exists for, reached through `arc-lead` (or directly by `arc-review-architect` when the finding is its own review's), never by a specialist mid-draft.
