# Room 02-research — Skills

> This room wields a focused subset of the 13 `/sofi-*` skills — Discovery is a single-gate room, so its skill use is narrower than the Boardroom's, but no less disciplined. This is the room's own reading of when each one fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | any of the seven, every session | First move, always — orients on `STATE.md`+`HANDOFFS.md`+`CONTEXT.md` before touching a persona, a map, or a citation. No specialist here acts on memory of a prior session. |
| `/sofi-delegate` | `res-lead` | Turning a raw Gate-1 kickoff intent (from `str-lead`'s frozen Problem Statement) into a paste-ready four-field Work Order for one of the five specialists, before spawning them. |
| `/sofi-team` | `res-lead` | Confirming which specialist owns a given piece of Discovery work before drafting the Work Order — e.g. distinguishing a `res-data-researcher` job (numbers) from a `res-web-scout` job (a single cited fetch) when the line is blurry. |
| `/sofi-gate` | `res-lead` | The Gate-1 advance decision itself: mechanical `sofi gate-check` plus `gtw-gatekeeper`'s fresh-context adversarial verdict — the room never self-grades its own freeze. |
| `/sofi-audit` | `res-lead` (rare, mostly on a Gate-8 loop-back) | A layered inspection of what already exists in the brain/codebase before re-researching from scratch on a re-opened Discovery pass. |
| `/sofi-fix` | `res-lead` | Routing a `res-fact-checker` CONTRADICTED or load-bearing UNKNOWN verdict back to the specific specialist who needs to fix it, cheapest route that clears the bar. |
| `/sofi-report` | `res-lead` | Writing the Gate-1 status check-in for `brd-cpo` as a durable, evidence-backed record rather than a chat-only summary. |
| `/sofi-handoff` | all seven | Closing ritual on every unit of work: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Never skipped — a persona draft or a fact-check pass left uncommitted is invisible to the next session. |

Skills this room does **not** typically wield: `/sofi-spec-review` and `/sofi-secure` (Gate-3+ concerns, owned by `04-architecture` and `09-security`), `/sofi-design-taste` (Gate-2, `03-design`'s instrument), `/sofi-feature` (full-loop orchestration, a Boardroom/`brd-ceo` commission that may *route into* this room's Gate-1 work but isn't wielded by the room itself), `/sofi-reflect` (scheduled dreaming, `knw-reflector`'s job — this room's HANDOFFS history is input to it, not something it runs itself).

## Rules

- `/sofi-boot` and `/sofi-handoff` bracket every single unit of work in this room, no exception — Discovery artifacts are exactly the kind of evidence-heavy output that's expensive to reconstruct from memory if a session ends uncommitted.
- `res-lead` is the only member who typically invokes `/sofi-gate`, `/sofi-delegate`, `/sofi-team`, `/sofi-fix`, and `/sofi-report` — consistent with the Room Isolation Law, cross-room-facing skill use flows through the gateway, not through individual specialists.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points and the sanitized-external-only rule (Article 07 §3) — this room's research findings never leave sanitized, and a genuinely contested UNKNOWN verdict is exactly the kind of decision point the oracle desk exists for.
