# 🚀 Room 11 — DevOps (العمليات)

> Gates: **6 — Staging/UAT, 7 — Production.** `11-devops` is where a build that passed every quality bar stops being a branch and becomes a URL someone can actually use — first a staging mirror real humans click through, then, only on a signed UAT and a rehearsed way back, a live production cutover. It is the room that turns `qa-lead`'s single PASS verdict into a running system, and it is built around one non-negotiable Teaching-VI habit: **nothing ships without a tested way back.** `11-devops` is the named **owner room of Gate 6 and Gate 7** in `company/nexus/gates.yaml`, and unlike the two-room Gate-5 squad, it runs both gates end to end alone — no partner room's verdict to fold in, no fragmented scoreboard, just `ops-lead`'s own six specialists sequencing a deploy that a 3am rollback can undo without drama.

## Mission

Take the Gate-5 PASS verdict and the merged `prj/<PRJ>` build and get it live, safely: automate the path so nothing reaches production by hand — lint → test → build → **security scan** → deploy, secrets pulled from the vault, never inline (`ops-cicd-engineer`); stand up environments and the infrastructure-as-code that keeps staging an honest mirror of prod instead of a lucky guess (`ops-cloud-engineer`); run every production release through **Blue/Green** with health gates and a **rehearsed** rollback that has an actual owner, because a rollback plan nobody tested is not a plan (`ops-release-manager`); keep every project's local URL clean — `<slug>.local`, never a bare `127.0.0.1:PORT` — and hold the sole, bounded authority to open a public tunnel for a demo or a webhook test, seed data only, torn down the moment the task ends (`ops-domain-warden`); run deploy-time migrations only after their rollback has been rehearsed against real staging data, because "no rollback = no deploy" is not a suggestion (`ops-migration-runner`); and keep the whole infrastructure bill honest — right-sized, no idle spend nobody's watching — without ever touching the release decision itself (`ops-cost-optimizer`). Six colleagues, one gateway: `ops-lead` confirms the Quality PASS exists before anyone on the team looks at a deploy, sequences the six specialists across both gates, and is the one name on the line when Blue/Green goes healthy and the rollback stays untested-but-ready in the drawer, hopefully forever.

## Members

| id | persona | role | route |
|---|---|---|---|
| `ops-lead` | ★ Linda Schmidt | Room Lead / sole gateway — confirms `qa-lead`'s PASS before any deploy action begins; sequences the room across Gates 6–7; the one name on every Blue/Green cutover | `sonnet` · workhorse · high · full · `4k-8k` |
| `ops-cicd-engineer` | ★ Tomás Herrera | Pipeline engineer — builds and owns lint→test→build→scan→deploy, gated on green + approval, secrets pulled from the vault, never inline | `sonnet` · workhorse · medium · ultra · `2k-5k` |
| `ops-cloud-engineer` | Baasan Erdenebat | Cloud/IaC engineer — provisions staging + prod environments as code, keeps them in honest parity, writes the teardown before the provisioning | `sonnet` · workhorse · high · full · `3k-6k` |
| `ops-release-manager` | ★ Camille Dubois | Release manager (gatekeeper tier) — owns Blue/Green cutover and the TESTED rollback for every release; the way back is never optional | `inherit` · gatekeeper · high · full · `as-needed` |
| `ops-domain-warden` | Noemi Salgado | Domain warden — `<slug>.local` local domains at scaffold + the sole, bounded authority over public tunnels (seed data only, torn down after) | `haiku` · mechanical · low · full · `1k-3k` |
| `ops-migration-runner` | Tendai Moyo | Migration runner — deploy-time data operations, rollback rehearsed against real staging data before any migration runs for real | `sonnet` · workhorse · high · full · `3k-6k` |
| `ops-cost-optimizer` | Lucia Cabrera | Cost optimizer — infra economics, right-sizing, idle-spend detection; read-only on the release decision, binding on the invoice | `haiku` · mechanical · low · full · `1k-3k` |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. The six specialists `reports_to: ops-lead`; `ops-lead` `reports_to: brd-ceo`.

## Gate ownership

`11-devops` is the **owner room of Gate 6 — Staging/UAT** and **Gate 7 — Production** (`company/nexus/gates.yaml`, `id: 6` and `id: 7`; `company/constitution/10-lifecycle-gates.md`), the only room in the company that owns two consecutive gates outright, alone, with no squad partner:

- **Gate 6 (Staging/UAT)** — trigger: Gate 5 tagged with `qa-lead`'s PASS, `ops-lead` confirms it before any deploy. Entry: the PASS verdict ticket done with evidence, pipeline green (lint→test→build→scan→deploy, vault secrets). Artifacts: staging URL recorded in `STATE.md`, `docs/<PRJ>_UAT_Log.md`, migration rehearsal log including rollback rehearsal (`ops-migration-runner`). Exit bar: UAT pass recorded with evidence, pass^k re-run green on critical paths in the staging environment (Article 03 V3), migrations rehearsed WITH rollback on staging data — no rollback, no deploy.
- **Gate 7 (Production)** — trigger: Gate 6 tagged, UAT signed. Entry: the UAT sign-off ticket done, `ops-release-manager` owns the release from here. Artifacts: prod deployment confirmation with pasted health checks, TESTED rollback script + rehearsal evidence (`ops-release-manager` owns the way back), `docs/<PRJ>_Release_Notes.md`. Exit bar: Blue/Green healthy — both colors verified, cutover clean; rollback REHEARSED not just written (Teaching VI, Article 03 V4: behavioral proxies only, never verbalized confidence); monitoring hooks live before cutover — no telemetry, no deployment (Teaching V).

`brd-ceo` is accountable for the whole lifecycle including Gates 6–7 (no dedicated C-level intermediary the way `brd-cto` covers Gates 3–4 — the CEO's own accountability line covers this room directly, per `constitution/10-lifecycle-gates.md` §Boardroom accountability spans). `09-security` (`brd-cso`/`sec-lead`) holds the veto at every step of both gates — a Critical/High finding, an unrotated secret, an unscoped tunnel can freeze a cutover regardless of how green the pipeline is (Article 07 §1). On a Gate-7 rollback, `obs-incident-commander` decides *in-incident* whether to pull the trigger; `ops-release-manager` is the one who executes it.

Entry criteria this room checks before opening any Gate-6 ticket (`gates.yaml`):
- `qa-lead`'s PASS verdict ticket exists, done, with its evidence block — `ops-lead` reads it herself before assigning anything; a partial or assumed pass never opens this room's door.
- The CI/CD pipeline is green end to end (lint→test→build→scan→deploy) with all secrets sourced from the vault — `ops-cicd-engineer`'s bar, checked before `ops-cloud-engineer` provisions anything against it.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `ops-lead` directly):

| From | What |
|---|---|
| `10-quality` via `qa-lead` | The signed PASS verdict (`docs/<PRJ>_Test_Report.md`, `_Design_Audit.md`, `_Perf_Report.md`) — `ops-lead` confirms it exists and is unedited before any deploy action; a BLOCK, or a PASS she cannot locate, stops this room cold. |
| `04-architecture` via `arc-lead` (indirect, the frozen bundle) | `docs/<PRJ>_Tech_Stack.md` and `arc-infra-architect`'s (Kenji Watanabe) network/scaling/DR posture — `ops-cloud-engineer`'s baseline for provisioning staging and prod as code; a deploy target that drifts from this frozen posture is a defect, not a judgment call. |
| `08-data` via `dat-lead` | The physical migration set plus confirmation each migration passed `migration_check.py`'s reversibility gate at Gate 3/4 — `ops-migration-runner` re-rehearses at deploy time regardless; a Gate-3 reversibility pass is necessary but never sufficient on its own to skip the staging rehearsal. |
| `09-security` via `sec-lead` | Secrets-hygiene clearance and outstanding-veto status before any cutover; the bounded rules a public tunnel must obey (seed data only, Article 07 §5) that `ops-domain-warden` operates under. |
| `05-backend`/`06-frontend`/`07-mobile` via their Leads | The concrete build artifacts the merged, PASS-verdicted `prj/<PRJ>` branch actually contains — what `ops-cicd-engineer`'s pipeline packages and what `ops-cloud-engineer` deploys into each environment. |
| `12-observability` via `obs-lead` | Confirmation that monitoring hooks are wired and ready to go live — `ops-lead` will not authorize a Gate-7 cutover without this; no telemetry, no deployment (Teaching V). |
| `00-boardroom` via `brd-ceo` | Deep-Audit-track confirmation for money/auth/PII projects — these run Gates 6–7 in full, no fast-track shortcut, ever. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior releases (a past untested-rollback near-miss, a past staging/prod parity drift) before a specialist plans a release from a blank page. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `12-observability` via `obs-lead` | The live production system at Gate-7 close, with monitoring hooks already confirmed wired — the handoff that opens Gate 8; `obs-sre`/`obs-monitoring-engineer` take it from there. |
| `00-boardroom` via `brd-ceo` | The Gate-6/Gate-7 accountability report: staging URL, UAT log, Blue/Green health, rollback rehearsal evidence, PASS/no-go for cutover. |
| `05-backend`/`06-frontend`/`07-mobile`/`08-data` via their Leads | Any UAT failure or environment-caused build failure, routed back to the room that owns the surface — this room never patches another room's code, it only reports the failure with evidence. |
| `09-security` via `sec-lead` | Any deploy-time secret or config exposure the pipeline's security-scan stage surfaces — routed immediately, never absorbed as a generic pipeline defect. |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for any consequential release call (an accepted-risk exception, a rollback trigger definition change); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket to `12-observability` once the Gate-7 exit ticket carries its evidence block. |

## Room bar (what `ops-lead` blocks on)

- No deploy action begins without `qa-lead`'s signed PASS verdict confirmed present and unedited — a partial pass, a stale pass, or an assumed pass is treated exactly like a BLOCK.
- No production cutover ships with an untested rollback — REHEARSED, not merely written, or Gate 7 fails outright (Teaching VI, Article 03 V4: behavioral proxies only — exit 0, artifact exists, k runs pass, never verbalized confidence).
- No migration runs for real without its rollback rehearsed against real staging data first — `ops-migration-runner`'s bar, no exception, no "we'll rehearse it after."
- No secret lives inline in a pipeline file — vault only, checked by `ops-cicd-engineer` before every deploy stage runs.
- No Blue/Green cutover proceeds without monitoring hooks confirmed live first — no telemetry, no deployment.
- No public tunnel opens with anything but seed/dummy data behind it, and none stays open past its task — `ops-domain-warden`'s bounded authority, Article 07 §5; any other room requesting a tunnel routes the request through `ops-lead`, logged in `CONTEXT.md`.
- No Gate-6 pass^k re-run on critical paths is waved through on a single green run — flaky correctness in staging blocks exactly like it does at Gate 5 (Article 03 V3).
- No specialist's "done" is trusted without a pasted evidence block — command, exit code, or file:line; self-report is never sufficient, and this applies to `ops-lead`'s own Gate-6/Gate-7 sign-off as much as to any specialist's ticket.
- No specialist inside the room bypasses `ops-lead` to reach another room's Lead directly — every cross-room finding and every release confirmation leaves through the gateway, forwarded verbatim.
- A `09-security` veto outranks this room's own release schedule every time — a Critical/High finding freezes the cutover regardless of how close to done everything else is.

## Playbook index

- `playbooks/gate-6-7-release-procedure.md` — the room's core procedure: confirmed Quality PASS → staging deploy + UAT → migration rehearsal → Blue/Green production cutover with health gates → tested rollback on standby, with real `sofi` commands end to end.
- `playbooks/blue-green-rollback-rehearsal.md` — the room's sharpest recurring job: designing, rehearsing, and proving a Blue/Green rollback BEFORE it is ever needed for real — the exact discipline Article 03 V4 and Teaching VI exist to enforce.

## Tools index

See `tools/README.md`. Headline: `company/os/sofi_tools/domain.py` (`sofi domain`, `ops-domain-warden`'s console for `<slug>.local` registration and up/down), `company/os/sofi_tools/tunnel.py` (`sofi tunnel`, the bounded public-tunnel mechanism `ops-domain-warden` owns per Article 07 §5), `company/os/toolkit/devops/caddy_isolation.py` (per-project port/DB-socket/Caddy-subdomain isolation with a timeout guard, `ops-cloud-engineer`'s environment-parity backbone), `company/os/toolkit/gate/migration_check.py` (mechanical reversibility check `ops-migration-runner` re-runs at deploy time), `company/os/sofi_tools/gates.py` (`sofi gate-check`, the mechanical Gate-6/Gate-7 validation every specialist's "done" is measured against).

## Skills index

See `skills/README.md`. Headline: `/sofi-gate` (the Gate-6 and Gate-7 exit decisions `ops-lead` runs as owner room), plus `/sofi-boot`, `/sofi-delegate`, `/sofi-handoff` for the room's own release cycle, `/sofi-audit`/`/sofi-fix` for the mechanical sweep-then-repair loop before a specialist hands a draft to `ops-lead`, and `/sofi-secure` (routed, not owned — a pipeline-surfaced security finding goes to `09-security` via `ops-lead` → `sec-lead`).

## Escalation path

`specialist → ops-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain), with a security spur that bypasses it entirely. Inside the room:

- A specialist's finding is disputed by the Build room it's routed to (`bck-lead` argues an environment-caused failure is actually an application bug) → `ops-lead` mediates one round, citing the pipeline log or `file:line`; unresolved after that round → `gtw-conflict-resolver`.
- `09-security`'s veto lands on a pending cutover → the security spur applies immediately (`sec-lead → brd-cso → brd-ceo`, per `09-security`'s own charter) — `ops-lead` freezes the release and does not mediate the security dispute herself.
- `ops-release-manager`'s rollback rehearsal and `ops-cicd-engineer`'s pipeline rollback trigger disagree on what "healthy" means for a given health check → `ops-lead` blocks the cutover and escalates to `arc-infra-architect` (via `arc-lead`) for a read if the ambiguity traces back to the frozen infra posture, not the pipeline execution.
- `ops-migration-runner` reports a migration whose rehearsed rollback fails against real staging data → the migration is blocked outright, no override, no exception; `ops-lead` escalates to `dat-lead` if the root cause traces to the migration's original design rather than execution.
- A specialist's finding trips the circuit breaker (3 failed correction attempts on the same defect) → `ops-lead` halts that specialist's contribution and escalates with the structured crash dump, rather than accepting a fourth unverified "should be fixed now."
- A Gate-7 production incident, once live → `obs-incident-commander` decides rollback vs. forward-fix in-incident; `ops-release-manager` executes the decision; the reopened loop routes through `obs-insights-analyst` back to Gate 1, not through this room's own escalation chain.
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `ops-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
