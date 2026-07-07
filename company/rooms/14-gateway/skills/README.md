# Room 14-gateway — Skills

> This room is unusual among the fifteen: several `/sofi-*` skills are not just *wielded* by `14-gateway`, they are effectively *owned* by it — `/sofi-gate` runs on `gtw-gatekeeper`'s verification logic, and every other room's `/sofi-delegate` produces a Work Order shaped exactly the way `gtw-dispatcher` needs to route it. This is the room's own reading of when each skill fires from *this* room's seat, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-gate` | `gtw-gatekeeper` (the skill's actual engine) | Every gate-advancement request in the company — `sofi gate-check` (mechanical) + `gtw-gatekeeper`'s fresh-context adversarial verdict against the ORIGINAL `exit_bar` (Article 03 V2). This is the skill this room exists to run; `playbooks/gate-advancement.md` is its step-by-step form. No other room's Lead runs this skill's adversarial layer themselves — they request it through the standing gateway-reach exception. |
| `/sofi-delegate` | `gtw-dispatcher` | Turning a raw Work Order into a paste-ready RCCF block addressed to the correct room Lead — `gtw-dispatcher`'s primary tool for every cross-room dispatch. Every other room's own `/sofi-delegate` use produces the same shape this room consumes, which is exactly why the ticket schema (`nexus/bus/ticket-schema.md`) is binding company-wide rather than per-room. |
| `/sofi-team` | `gtw-dispatcher` | Confirming which room and which Lead actually owns a piece of incoming work before addressing it — the who-does-what lookup run before every dispatch, especially on an ambiguous Work Order that could plausibly land in more than one room. |
| `/sofi-boot` | every `gtw-*` agent, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a route, a verdict, an oracle send, a mediation, or a budget audit. No Gateway agent acts on memory of a prior session's state. |
| `/sofi-handoff` | every `gtw-*` agent | Closing ritual on every dispatch, route stamp, verdict, oracle-desk digest, mediation ruling, and audit: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. |
| `/sofi-reflect` | none directly (consumer, not owner) | `knw-reflector` owns the distillation itself, on `brd-ceo`'s schedule — but this room is one of its richest signal sources: `gtw-budget-warden`'s circuit-breaker trip ledger and `gtw-conflict-resolver`'s mediation rulings are exactly the recurring-pattern raw material `/sofi-reflect` mechanically locates and turns into `LESSONS.md` entries. |
| `/sofi-report` | `gtw-budget-warden`, `gtw-external-reviewer` | `gtw-budget-warden`'s weekly waste audit and `gtw-external-reviewer`'s oracle-desk digests are exactly the kind of durable, evidence-backed writeups this skill exists to produce for the boardroom rather than letting them live only in chat. |
| `/sofi-audit` | none directly | This room holds no product-code or design surface to audit — `/sofi-audit`'s layered sweeps (`ui`/`css`/`db`/`api`/`agents`/`all`) are consumed BY this room (`gtw-gatekeeper` may read an audit's findings as part of a gate-check's evidence trail) but never triggered by it. |
| `/sofi-spec-review` | none directly | Owned by `04-architecture`'s `arc-review-architect`; this room is occasionally a *subject* when a cross-layer review's Tier-A verdict is itself a gate-advancement question `gtw-gatekeeper` rules on, but never the trigger. |
| `/sofi-secure` | none directly (routed) | Security findings surfaced during a gate-check or a mediation route immediately to `sec-lead`/`brd-cso` (the security spur) — this room never runs the security squad itself, it only ensures the finding doesn't get lost in transit. |
| `/sofi-fix` | none directly | Findings this room surfaces (a FAIL verdict's exact gap, a budget-waste flag) route to the owning specialist via that specialist's own room Lead for repair — `14-gateway` diagnoses and verifies, it does not fix. |
| `/sofi-feature` | none directly | The full end-to-end loop belongs to whichever room owns the feature's surface; this room's `/sofi-gate` engine is one stage inside that loop, never the whole thing. |
| `/sofi-design-taste` | none | No design surface in this room. |

## Rules

- `/sofi-gate`'s adversarial layer is reachable only through `gtw-gatekeeper` — no other agent in the company, including this room's own `gtw-dispatcher`, self-certifies a gate verdict. The standing gateway-reach exception lets any Lead *request* the check; it never lets anyone skip it.
- `gtw-external-reviewer` is the only agent in this room holding `WebSearch`/`WebFetch` — every oracle-desk send is sanitized first (Article 07 §3), and the desk's reply is advisory, never a substitute for `gtw-gatekeeper`'s verdict or `gates.yaml`'s `exit_bar`.
- Every skill invocation in this room still obeys the Oracle Loop (Teaching VII) at its own decision points — a contested UNKNOWN verdict on a money/auth/PII surface, or a mediation that can't resolve in one round, is exactly the kind of decision point `gtw-external-reviewer`'s desk and `brd-arbiter`'s formal protocol exist for.
- `gtw-router` and `gtw-budget-warden` never invoke a skill that spends more than a mechanical-tier lookup — their whole mandate is the discipline this room enforces on everyone else, and a warden or a router burning workhorse-tier tokens on its own routine work is the exact waste pattern `gtw-budget-warden`'s own audit would flag.
