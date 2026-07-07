# Room 11-devops — Skills

> `11-devops` is the room that turns a signed Quality PASS into a live production system — it wields the boot-and-close ritual skills every Gate-6/Gate-7 pass and is the sole owner of the local-domain-and-tunnel boundary (Article 07 §5), even though that boundary is operated through `sofi domain`/`sofi tunnel` rather than a `/sofi-*` palette skill. This is the room's own reading of when each skill fires, not a duplicate of the skill files themselves (`.claude/skills/sofi-*/`).

## Skills this room wields, and when

| Skill | Wielded by | When |
|---|---|---|
| `/sofi-boot` | every `ops-*` agent, every session | First move, always — orients on `STATE.md` + `HANDOFFS.md` + `CONTEXT.md` before touching a staging deploy or a production cutover. No DevOps agent authorizes a release on memory of a prior one. |
| `/sofi-gate` | `ops-lead` (owner, both gates) | The room's core, standing job: running the Gate-6 and Gate-7 exit decisions — mechanical `sofi gate-check --gate 6|7` plus `gtw-gatekeeper`'s fresh-context adversarial verdict against the ORIGINAL exit bar in `gates.yaml`. Never a self-graded "looks healthy to me." Binding procedure: `playbooks/gate-6-7-release-procedure.md`. |
| `/sofi-delegate` | `ops-lead` | Turning a Gate-6 or Gate-7 dispatch into a paste-ready four-field Work Order for the specialist who owns the next piece — pipeline first (`ops-cicd-engineer`), then environment (`ops-cloud-engineer`), then migration rehearsal (`ops-migration-runner`), then the cutover itself (`ops-release-manager`), in that order, never out of sequence. |
| `/sofi-team` | `ops-lead` | Confirming which of the room's six specialists owns a given release-time question before drafting the Work Order — especially when a failure straddles two specialists (an environment-shaped failure that might actually be a pipeline health-check misconfiguration). |
| `/sofi-handoff` | every `ops-*` agent | Closing ritual on every artifact: checkpoint → `CONTEXT.md` → `STATE.md` `head_sha` → next ticket in `HANDOFFS.md`. Runs after every specialist's step is accepted by `ops-lead`, and again at each gate's own close (Gate 6, then separately Gate 7). |
| `/sofi-audit` | `ops-lead` (requests), the relevant specialist (executes) | A per-layer sweep before a release-time draft is trusted — e.g. a wiring/security-shaped sweep of the pipeline config before `ops-cicd-engineer` hands it to `ops-lead`. Findings route into the same ticket the specialist is already closing, never a separate detour. |
| `/sofi-fix` | routed, rarely executed directly in this room | Most fixes this room surfaces belong to another room's Lead (an environment-caused failure that's actually an application bug) — `ops-lead` routes them there. When a fix is genuinely this room's own (a pipeline stage misconfiguration, a Caddy vhost drift), the owning specialist applies it directly and re-verifies with `/sofi-gate`. |
| `/sofi-report` | `ops-lead` | Writing the Gate-6/Gate-7 accountability check-in for `brd-ceo` as a durable, evidence-backed record (`/sofi-report devops`) rather than letting the release's story live only as a raw ticket in `HANDOFFS.md`. |
| `/sofi-secure` | none directly (routed, never executed here) | A pipeline-surfaced security finding (a scan-stage hit, a secret found inline) never gets triaged inside this room — `ops-lead` routes it to `09-security` via `sec-lead` immediately; this room supplies the finding's location and evidence, `09-security` supplies the judgment. |
| `/sofi-spec-review` | none directly (consumed, not owned) | Owned by `04-architecture`'s `arc-review-architect`. If a release-time failure traces back to the original infra design rather than this room's execution, `ops-lead` escalates for a spec-review read rather than patching around a design gap. |
| `/sofi-reflect` | none directly | The room contributes the sharpest possible signal (a recurring untested-rollback near-miss, a repeated staging/prod parity drift, a circuit-breaker trip on a stuck migration rehearsal) but does not execute the distillation itself — that's `knw-reflector`'s job on `brd-ceo`'s schedule. |

## The domain/tunnel console — mechanics, not a `/sofi-*` skill

`sofi domain` and `sofi tunnel` (`company/os/sofi_tools/domain.py`, `tunnel.py`) are CLI verbs, not palette skills, and `ops-domain-warden` is their sole standing operator per Article 07 §5. `sofi domain register/up/down/list/status` runs at Gate 0 (scaffold) and again at Gate 6 (bringing staging live); `sofi tunnel up/down/list/status` runs only on a named, time-boxed task — a demo, a webhook test — never as a substitute for the Gate-6/Gate-7 deploy path itself. Any other room's request for either routes through `ops-lead` first, logged in `CONTEXT.md`.

## Rules

- `11-devops` never invokes `/sofi-feature` itself — that is a Boardroom-commissioned, cross-gate skill; this room supplies its Gate-6/Gate-7 slice when `brd-ceo` runs the full loop, but never triggers the whole arc.
- `ops-lead` never invokes `/sofi-audit` on another room's layer — that is a per-layer sweep owned by whichever room's Lead requests it; this room's own use of `/sofi-audit` stays inside its own pipeline/environment/release artifacts.
- The tunnel boundary (`company/constitution/07-security-law.md` §5) is **not** a skill invocation — it is a standing authority `ops-domain-warden` exercises directly, with no `/sofi-*` command gating it. A `/sofi-secure scan` finding is frequently what *triggers* a tunnel being refused or torn down early, but the authority itself has no palette command.
- Every skill invocation still obeys the Oracle Loop (Teaching VII) at its own decision points — a contested "is this rollback actually rehearsed enough" call, or a release-readiness judgment under real schedule pressure, is exactly the kind of decision point `gtw-external-reviewer`'s desk exists for, reached through `ops-lead`, never by a specialist mid-cutover.
- Deploy and rollback confirmations through any skill are always normal prose — no `caveman` compression on an irreversible action, ever, regardless of which skill produced the status line around it.
