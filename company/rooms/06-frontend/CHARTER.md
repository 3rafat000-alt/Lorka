# 🖥️ Room 06 — Frontend (الواجهة الأمامية)

> Gate: **4.** The Frontend room is where the frozen Gate-3 contract and the frozen Gate-2 prototype stop being documents and become a screen a real hand can touch: typed components wired to `OpenAPI.yaml`, styled from `Design_Tokens.md`'s taste dials, moving under `prefers-reduced-motion`'s rules, reachable end to end by keyboard, and fast. Frontend runs as one of three parallel squads behind the *same* frozen bundle — `05-backend` and `07-mobile` build their own surfaces off the identical contract, none waiting on another's output to start. Nothing this room ships merges to `prj/<PRJ>` without clearing its own fresh-context review first; nothing reaches `10-quality` that `fnt-lead` hasn't gate-merged with evidence.

## Mission

Take the frozen Gate-3 bundle (`OpenAPI.yaml` + `Tech_Stack.md` + `Threat_Model.md`) and the frozen Gate-2 record (`Prototype_Spec.md` + `Content_Strings.json` + `Design_Tokens.md` + `A11y_Matrix.md`) and build the client-side surface: typed components in whichever framework `arc-system-architect` chose (Vue3+Pinia or React+typed service layer — never both on the same project), styled with Tailwind against the taste dials, animated with micro-interactions that degrade honestly under `prefers-reduced-motion`, verified WCAG 2.2 AA in the actual DOM (not just the design-phase matrix), and held inside its stated bundle-budget and Core Web Vitals. Eight colleagues, one gateway: `fnt-lead` decides which of the two component engineers the project needs, sequences the other five specialists behind that choice, checks every diff against the frozen contract and the frozen prototype, confirms `fnt-code-reviewer`'s fresh-context V2 pass before merging, and gate-merges the worktree — never before.

## Members

| id | persona | role | route |
|---|---|---|---|
| `fnt-lead` | ★ Grace Achieng | Room Lead / sole gateway — picks Vue vs React per the frozen stack, sequences the room, checks every diff against the frozen contract + prototype, gate-merges the worktree at close | `workhorse` · high · full |
| `fnt-vue-engineer` | Yūki Sato | Vue3 components + Pinia state, typed props, wired to the frozen contract — dispatched only when `Tech_Stack.md` names Vue | `workhorse` · medium · ultra |
| `fnt-react-engineer` | Marisol Vega | Typed React components + a typed service layer matching `OpenAPI.yaml` — dispatched only when `Tech_Stack.md` names React | `workhorse` · medium · ultra |
| `fnt-css-artisan` | Bjørn Halvorsen | Tailwind styling, responsive 320→1200+, taste dials applied faithfully, anti-generic-UI checklist in code | `workhorse` · medium · ultra |
| `fnt-interaction-engineer` | Noor Al-Rashid | Micro-interactions and motion implementation, `prefers-reduced-motion` fallback for every one, no bare removal | `workhorse` · medium · full |
| `fnt-a11y-engineer` | Amara Osei | WCAG 2.2 AA enforced in the actual DOM — focus order, ARIA, contrast, keyboard-completeness — the code-level guarantee behind Design's matrix | `workhorse` · medium · full |
| `fnt-performance-engineer` | Priyanka Deshmukh | Bundle budgets, code-splitting, Core Web Vitals (LCP/INP/CLS), baseline discipline | `workhorse` · medium · full |
| `fnt-code-reviewer` | Henrik Baumgartner | Fresh-context adversarial diff review (V2) — the last gate before `fnt-lead` merges anything | `workhorse` · medium · review |

Routes are copied verbatim from `company/nexus/routing.yaml` (`routes.<id>`) — this table is a convenience mirror, never the source. All seven specialists `reports_to: fnt-lead`; `fnt-lead` `reports_to: brd-ceo`.

## Gate ownership

`06-frontend` is a **squad member** (not the owner room) of **Gate 4 — Build** (`company/nexus/gates.yaml`, `id: 4`, `owner_room: 05-backend`), running alongside `05-backend` and `07-mobile` as three parallel worktree squads behind the *same* frozen Gate-3 bundle, with `08-data` as a support room for the physical migrations/cache/ETL work the frontend never touches directly (`effort_scaling.cross-room`):

- `05-backend` (owner room, via `bck-lead`) — endpoints, domain logic, Blade markup this room's components hydrate into, per the SOFI stack default (Laravel Blade + Vue3 islands).
- `06-frontend` (this room) — the interactive client-side surface: components, styling, motion, in-code accessibility, performance.
- `07-mobile` (via `mob-lead`) — the same frozen contract, built for Flutter; no direct dependency on this room's output.
- `08-data` (support, via `dat-lead`) — `dat-db-engineer` executes the physical migrations `04-architecture` designed; this room reads the resulting schema shape only through the frozen `OpenAPI.yaml`, never the raw migration files.

`brd-cto` (Ingrid Voss) is accountable for the Gate 3–4 span at the Boardroom level; `fnt-lead` signs this room's slice of the Gate-4 merge and reports status, `bck-lead` owns the aggregate Gate-4 exit ticket that folds all three squads' merges together.

## Interfaces

**Consumes-from** (by room, always through that room's Lead — Room Isolation Law, Article 00; Boardroom and Gateway may address `fnt-lead` directly):

| From | What |
|---|---|
| `04-architecture` via `arc-lead` | The frozen Gate-3 bundle: `OpenAPI.yaml` (the contract every service-layer call matches byte-for-byte), `Tech_Stack.md` (names which framework this room builds — Vue or React, never both), `Threat_Model.md` (auth/session assumptions the client must honor, e.g. token refresh flow). Not frozen → reject upward, don't build against a moving contract. |
| `03-design` via `dsn-lead` (frozen Gate-2 record, read directly from `docs/` once the `gate-2-done` tag exists; `dsn-lead` addressed only for a fidelity question the frozen record itself can't answer) | `Prototype_Spec.md` (every screen state — empty/loading/error — 1:1 journey mapping), `Content_Strings.json` (every UI string; none invented downstream), `Design_Tokens.md` (+ the three taste dials and named brand preset), `A11y_Matrix.md` (the WCAG 2.2 AA criteria per screen this room's code has to actually satisfy). |
| `05-backend` via `bck-lead` | The server-rendered markup structure this room's components hydrate into (per the Blade+Vue3 default), and live endpoint behavior confirmation when a contract ambiguity surfaces mid-build — the same frozen worktree wave, not a new request cycle. |
| `07-mobile` via `mob-lead` | Cross-platform consistency notes when a design token or interaction pattern needs to read identically on web and Flutter (rare, informational, never blocking). |
| `00-boardroom` via `brd-cto` | Gate-4 accountability checks; occasional binding constraints (a browser-support floor, a bundle-size ceiling) that bear on the framework or tooling choice. |
| `13-knowledge` via `knw-lead` | `LESSONS.md` procedural memory on comparable prior builds (a past `store-with-two-owners`-shaped mistake, a past reduced-motion regression) before a specialist writes from a blank file. |
| `10-quality` via `qa-lead` (post-hoc, later gate) | `Design_Audit.md` and `Perf_Report.md` findings from the Gate-5 pass, fed back as fix tickets when a fidelity or performance regression is found after merge. |

**Produces-to** (by room, through that room's Lead unless the target IS the Lead):

| To | What |
|---|---|
| `05-backend` via `bck-lead` | This room's merge readiness into the shared `prj/<PRJ>` integration branch (Gate-4 close is `bck-lead`'s aggregate call across all three squads); any contract-gap finding discovered mid-build, reflected back verbatim rather than worked around client-side. |
| `10-quality` via `qa-lead` | The merged `src/frontend/**` + test suite, `docs/<PRJ>_Frontend_A11y_Audit.md`, `docs/<PRJ>_Frontend_Perf_Baseline.md` — the surface `qa-design-auditor` and `qa-perf-analyst` check fidelity and budget against at Gate 5. |
| `00-boardroom` via `brd-ceo` (report) / `brd-cto` (accountability check) | This room's Gate-4 status: merge confirmation, evidence block, any open risk. |
| `13-knowledge` via `knw-lead` | `DECISIONS.md` ADR entries for every expensive-to-reverse call (Vue vs React confirmation, a state-management pattern, a bundle-splitting strategy); `HANDOFFS.md` ticket queue entries. |
| `14-gateway` via `gtw-router` | The next-gate ticket once this room's merge carries its evidence block. |

## Room bar (what `fnt-lead` blocks on)

- No merge without `OpenAPI.yaml` byte-parity verified in the service layer — a null-accessor client, an untyped response shape, or a silently-swallowed error branch is a rejected diff, not a follow-up ticket.
- All three states — empty / loading / error — built per the frozen `Prototype_Spec.md` for every screen this room touches; a screen missing a state is a rejected diff (Teaching I: no journey-less shortcut).
- Zero unresolved `fnt-a11y-engineer` findings in the actual DOM before merge — Design's `A11y_Matrix.md` states the intent, this room's own in-code check is the guarantee that actually ships.
- Every micro-interaction from `fnt-interaction-engineer` ships with a working `prefers-reduced-motion` fallback that preserves the information the motion conveyed — a bare removal that drops the cue is a fail, not a pass.
- Bundle budget and Core Web Vitals (LCP/INP/CLS) within `fnt-performance-engineer`'s recorded thresholds before merge — "we'll optimize later" is not a recorded baseline.
- Taste dials from `Design_Tokens.md` applied faithfully by `fnt-css-artisan` — never re-interpreted, never defaulted to the framework's out-of-the-box look.
- No diff merges without first passing `fnt-code-reviewer`'s fresh-context adversarial review (V2) — `fnt-lead` gate-merges the worktree only after that verdict, never before, never with `--no-ff` skipped.
- No specialist inside the room reaches `bck-lead`/`mob-lead`/`dsn-lead` directly — every cross-room artifact leaves through `fnt-lead`, forwarded verbatim, never re-authored.

## Playbook index

- `playbooks/gate-4-frontend-build.md` — the room's core procedure: frozen bundle → framework pick → component build (styling, motion, a11y, performance layered in) → fresh-context review → signed Gate-4 merge, with real `sofi` commands end to end, run alongside the `05-backend`/`07-mobile` squad.
- `playbooks/a11y-performance-hardening.md` — the room's sharpest recurring specialty: the pre-merge hardening pass `fnt-a11y-engineer` and `fnt-performance-engineer` run together on every component before it reaches `fnt-code-reviewer`, closing the gap between "looks done" and "is done."

## Tools index

See `tools/README.md`. Headline: `company/os/agents/uiux/uiux_pipeline.py` (the shared design/taste/RTL/a11y static-pack scanner `fnt-css-artisan` and `fnt-a11y-engineer` run before a model ever reads a component), `company/os/agents/tier-3-quality/performance-load-analyst/perf_budget.py` (the Core Web Vitals budget gate `fnt-performance-engineer` self-checks against pre-emptively, owned by `10-quality` and enforced for real at Gate 5), `company/os/sofi_tools/gates.py` (`sofi gate-check`) and `company/os/sofi_tools/gitops.py` (`sofi worktree` / `sofi gate-merge`) for the room's own build-and-merge cycle.

## Skills index

See `skills/README.md`. Headline: `/sofi-boot`, `/sofi-delegate`, `/sofi-team`, `/sofi-gate`, `/sofi-handoff` for the room's own Gate-4 cycle, `/sofi-design-taste` for `fnt-css-artisan`'s taste-dial application, and `/sofi-fix`/`/sofi-report` for closing out a `spec-review` or `qa` finding routed back into this room.

## Escalation path

`specialist → fnt-lead → gtw-conflict-resolver → brd-arbiter → brd-ceo` (Article 00, the standard chain). Inside the room:

- `fnt-vue-engineer`'s or `fnt-react-engineer`'s component contradicts `fnt-css-artisan`'s token application (e.g. a hardcoded color the component owns instead of reading the token) → `fnt-lead` mediates first, one round, citing both `file:line` positions; unresolved after that round → `gtw-conflict-resolver`.
- A screen in the frozen `Prototype_Spec.md` has no built state (empty/loading/error) after a specialist's pass → `fnt-lead` rejects the diff and re-dispatches, rather than merging a partial screen on schedule pressure.
- `fnt-a11y-engineer` finds an unresolved WCAG 2.2 AA criterion after one correction round from the owning component engineer → `fnt-lead` blocks the merge and escalates to `dsn-lead` only if the gap traces back to an ambiguous or contradictory design spec, otherwise holds the block at the component engineer.
- `fnt-performance-engineer` finds a Core Web Vital or bundle-budget breach that survives one optimization round → `fnt-lead` blocks the merge; if the breach traces to a stack choice made at Gate 3 (e.g. an unavoidably heavy dependency), escalates to `arc-lead` rather than absorbing it silently.
- `fnt-code-reviewer` returns `UNKNOWN` on a diff it cannot decide from the evidence → `fnt-lead` escalates via `sofi escalate`, never forces the verdict to PASS; for a diff touching money, auth, or PII fields, route through the Gemini review desk (`gtw-external-reviewer`) as a family-diverse second opinion before treating a single-model PASS as final.
- A dispute above `gtw-conflict-resolver`'s mediation authority → `brd-arbiter`, one-line ADR, `fnt-lead` informed and the ruling forwarded verbatim to whichever specialist is affected.

Doctrine: **Design is Truth · few token do trick · big brain small mouth.** 🪨
