# Room 13-knowledge — Skills

> This room owns exactly one `/sofi-*` skill outright (`/sofi-reflect`) and is the quiet backbone under two more that every other room takes for granted (`/sofi-boot`'s brain read, `/sofi-handoff`'s write order) — it is the room least visible in the palette and most load-bearing underneath it. This is the room's own reading of when each skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-reflect` | `knw-reflector` (owner) | This room's one owned command — the scheduled dreaming pass. Fires at gate close, or on an explicit on-demand request; **never** mid-task, never per-turn (Article 04 rule 1). Runs `reflection_engine.py scan` first, then `write` per surviving candidate. Binding procedure: `playbooks/gate-close-reflection-and-hygiene.md`. |
| `/sofi-boot` | every `knw-*` agent, every session — and, indirectly, every agent in the company | First move, always, for this room's own agents. But `/sofi-boot`'s brain-read half (`MEMORY.md` + `LESSONS.md`) is what every *other* agent in the company reads on their own boot — this room is the one that keeps those two files worth reading, even though it never "runs" `/sofi-boot` on anyone else's behalf. |
| `/sofi-handoff` | every `knw-*` agent | Closing ritual on every artifact this room produces: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Also the write-order contract (`company/brain/BRAIN.md` §7) this room's own `knw-lead` polices company-wide as part of brain governance — an uncommitted memory pass is invisible to the next session, and `knw-lead` treats that as a room-bar violation regardless of which room left it open. |
| `/sofi-delegate` | `knw-lead` | Turning a cross-room memory-governance request or a gate-close dispatch into a paste-ready four-field Work Order for the specialist who owns the next piece — `knw-reflector` first at gate close, always, before `knw-memory-curator`'s hygiene pass runs. |
| `/sofi-team` | `knw-lead` | Confirming which of the room's five specialists owns a given piece of memory work before drafting the Work Order — especially when a request straddles two specialists (a gate-close pass that needs both a lesson distilled and a file compressed). |
| `/sofi-gate` | `knw-lead` | This room owns no numbered gate, so it never runs `/sofi-gate` as the deciding room — but it confirms via `sofi gate-check` that a gate genuinely closed before its own gate-close playbook (reflection + hygiene + history) runs, the mechanical trigger-confirmation step. |
| `/sofi-report` | `knw-lead` | Writing the room's own accountability check-in for `brd-ceo` — org-brain health, `MEMORY.md` line count, any open cross-room memory-governance dispute — as a durable, evidence-backed record rather than a chat-only status. |
| `/sofi-audit` | none directly (routed, never executed here) | This room is never the *target* of a layer audit (it has no code/UI/DB layer) — but a requesting room's Lead may ask `knw-brain-query` for retrieval support (prior findings, recurring patterns) feeding into someone else's `/sofi-audit` run. |
| `/sofi-secure` | none | Not this room's concern directly — a security-shaped finding surfaced during a reflection pass (a recurring credential-leak pattern, say) is flagged to `sec-lead` via the affected project's own room Lead, never actioned here. |
| `/sofi-fix` | none | This room diagnoses and remembers; it does not implement fixes. A `LESSONS.md` promotion candidate that would change a spec or template goes to `brd-ceo` for a decision, not to `/sofi-fix`. |
| `/sofi-feature` / `/sofi-spec-review` | none directly (consumed, not owned) | This room never triggers either — but `knw-brain-query` is frequently the fastest way for `arc-review-architect` or `brd-ceo` to confirm "has this exact spec-review finding come up before" before either skill runs its own sweep. |

## Rules

- `13-knowledge` never invokes `/sofi-feature` or `/sofi-spec-review` itself — those are Boardroom/Architecture-commissioned, cross-gate skills; this room supplies retrieval and memory support when asked, never triggers the arc.
- `/sofi-reflect` runs on trigger only — gate close or explicit on-demand — never as a background habit or a per-turn moralizing pass. A specialist elsewhere in the company who wants a lesson written immediately after a failure is redirected: the signal is recorded in the ticket now, the dreaming happens on `knw-reflector`'s schedule.
- `knw-lead` never bypasses another room's own Lead to dispatch a memory-governance ruling directly to a specialist — every finding and every ruling leaves through the gateway, forwarded verbatim (Room Isolation Law).
- Reflection output (`/sofi-reflect`'s lessons) is always full normal prose — no `caveman` compression on `LESSONS.md` content, ever, regardless of which skill produced the trigger.
- The Oracle Loop (Teaching VII) still applies at this room's own decision points — a `LESSONS.md` promotion candidate that would touch doctrine is exactly the kind of decision `brd-ceo` may route through the external review desk before ruling, reached through `knw-lead`, never by a specialist mid-draft.
