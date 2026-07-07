# Room 01-strategy — Skills

> Strategy is the first room to touch a new project, so it wields the boot-and-close ritual skills constantly and the heavier cross-cutting ones rarely — most of what this room produces is prose the room itself gate-checks, not code an audit sweep needs to locate. This is the room's own reading of when each `/sofi-*` skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | every `str-*` agent, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a raw idea. No Strategy agent drafts on memory, especially at Gate 0 where there's often barely any brain yet to read. |
| `/sofi-delegate` | `str-lead` | Turning `brd-chief-of-staff`'s raw intent, or a loop-back ticket from `res-lead`, into a paste-ready four-field Work Order for the specialist who owns that piece — `str-product-strategist` first, always, before anyone else fans out. |
| `/sofi-team` | `str-lead` | Confirming which of the room's six specialists (or, rarely, which agent in another room) owns a given piece of raw intent before drafting the Work Order — especially useful the first time a project's shape is ambiguous (is this a monetization question or a market-sizing question?). |
| `/sofi-gate` | `str-lead` | The Gate-0 exit decision itself: mechanical `sofi gate-check --gate 0` plus `gtw-gatekeeper`'s fresh-context adversarial verdict — never a self-graded sign-off. This is the room's single most load-bearing skill invocation. |
| `/sofi-handoff` | every `str-*` agent | Closing ritual on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Runs after every specialist's draft is accepted by `str-lead`, and again at the room's own Gate-0 close. |
| `/sofi-report` | `str-lead` | Writing the Gate-0 accountability check-in for `brd-ceo`/`brd-cpo` as a durable, evidence-backed record in the brain rather than a chat-only summary — especially on a Deep-Audit project where `brd-cso` needs a citable trail. |
| `/sofi-audit` | `str-lead` (rare) | Only when a brownfield project's existing codebase needs a quick health-read before `str-product-strategist` writes the Problem Statement — borrowed the same way `ceo_toolkit.py`'s `ProjectInspector` is borrowed, not a routine Strategy move. |
| `/sofi-reflect` | none directly | The room contributes signal (a Gate-0 rejection, a track call that got reopened at Gate 1) but does not execute the distillation itself — that's `knw-reflector`'s job on `brd-ceo`'s schedule. Worth knowing the room's own `HANDOFFS.md` history is exactly what feeds it. |

## Rules

- `01-strategy` never invokes `/sofi-spec-review`, `/sofi-secure`, `/sofi-fix`, or `/sofi-design-taste` — those are Gate 2+ and Gate 3+ skills, and this room's output is pre-code, pre-design prose. Reaching for one of them here is a sign the room has drifted past its own gate boundary.
- `/sofi-feature` is a Boardroom-commissioned, cross-gate skill; `01-strategy` supplies the Gate-0 slice of it when `brd-ceo` runs the full loop on a feature, but never triggers the whole arc itself.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points — a genuinely contested track call or a thin Problem Statement is exactly the kind of decision point `gtw-external-reviewer`'s desk exists for, reached through `str-lead`, never by a specialist directly.
