# 🎫 The Ticket — bus message schema (TKT blocks in `HANDOFFS.md`)

> **Foundation: implements Article 08 (`company/constitution/08-handoff-law.md`).** The bus is not middleware — it is ticket blocks appended to the project brain's `projects/<PRJ>/_context/HANDOFFS.md`, parsed by `sofi_tools.tickets`, validated fail-closed by `sofi gate-check`. This file is the binding schema; a block that doesn't parse doesn't exist.

## 1. The block

```md
## TKT-014 · gate 3
from: arc-system-architect
to:   dat-db-engineer
task: model entities for the audit-log journey; reversible migrations.
consumes: docs/PRJ-0001_Tech_Stack.md, docs/PRJ-0001_OpenAPI.yaml
expected: docs/PRJ-0001_Schema.sql + ERD + migrations(+rollback)
route: workhorse · high · full
status: open
```

**Header contract:** `## TKT-NNN · gate N` — parsed by `tickets.py` header regex (`^##\s*(TKT-\d+)\s*·?\s*gate\s*(\d)`). `TKT-NNN` is zero-padded and monotonic per project (`tickets.next_id`); the gate number must match the project's current gate or a declared loop-back — `validate_no_skip` reports anomalies.

## 2. Fields

| Field | Req | Meaning |
|---|---|---|
| `from:` | ✔ | Sending agent id (`<roomcode>-<role>`, per `nexus/registry.yaml`). |
| `to:` | ✔ | Receiving agent id. Must satisfy the room-boundary rule (§4). |
| `task:` | ✔ | Verb + object, one coherent deliverable — the Command seed of the Work Order (`constitution/01-work-order.md`). |
| `consumes:` | ✔ | The frozen upstream artifact(s) this work derives from, by path (+ §section when it matters). Not frozen → the receiver **rejects upward**, never improvises (Teaching I/II). |
| `expected:` | ✔ | Deliverable shape + exact paths under `projects/<PRJ>/…` — what `validate_artifacts` will check exists. |
| `route:` | ✔ | `model · effort · caveman`, copied **verbatim** from `nexus/routing.yaml` `routes.<id>` — never invented (`gtw-router` stamps it). |
| `status:` | ✔ | Lifecycle state, §3. |
| `type:` | – | Ticket kind: `build \| review \| audit \| escalation \| blocker \| re-open`. |
| `mem:` | – | Memory-type frontmatter (`semantic \| episodic \| procedural`) — routes `sofi brain-query` and reflection consolidation. |
| `date:` | – | Supplied by the CEO/caller — **never invented** (agents don't own the clock, `company/os/GOVERNANCE.md` rule 9). |
| `escalated_from:` | – | On an escalation ticket: the original `TKT-NNN` — keeps the chain traceable (§6). |

## 3. Lifecycle + the evidence block

```
open → accepted → done | rejected          (side path: blocked → escalated)
```

- **`open`** — filed, unclaimed.
- **`accepted`** — the receiver has read the ticket, verified its `consumes:` inputs exist **and are frozen**, and taken it. Acceptance of a `done` deliverable additionally requires a fresh-context check against the ORIGINAL ticket criteria (Article 03 V2) — never the producer's self-report.
- **`done`** — Definition of Done passed **with an evidence block appended to the ticket**. `sofi_tools.gates.validate_evidence()` scans done-tickets inside `sofi gate-check` and rejects, fail-closed, any that carry none. Accepted evidence forms (at least one): a fenced command block with its output and **exit code** · a test run showing `passing` · a `file:line` proof the artifact exists · a commit **SHA/diff**. Self-report is not evidence.
- **`rejected`** — bounced with a one-line reason; the ball goes back up. No silent proceed.
- **`blocked → escalated`** — the decision is above the holder's authority: `sofi escalate <PRJ> <TKT> <to> "<reason>"` files an up-chain ticket carrying `escalated_from:` and flips this one. Mechanics: `nexus/bus/escalation.md`.

`sofi handoff <op> <ID>` and `sofi dispatch` operate the queue; `sofi brain-query` filters on `type:`/`mem:`.

## 4. The room-boundary rule (Isolation Law, wired)

A ticket's `from:`/`to:` pair is valid **only** if it is one of:

1. **Same room** — `bck-api-engineer → bck-code-reviewer`.
2. **Agent ↔ its own Lead** — `dat-db-engineer → dat-lead`.
3. **Lead ↔ Lead** — `arc-lead → dat-lead` (the only legal room crossing).
4. **Boardroom (`brd-*`) or gateway (`gtw-*`) ↔ any Lead.**

A specialist never addresses a specialist in another room — not even "just a quick question." Cross-room work is a request to your own Lead, forwarded Lead-to-Lead **verbatim** (citations + evidence intact — no translation tax), assigned internally; the answer returns the same path. Enforced by `sofi_tools.tickets.validate_room_boundary()` (agent→room map loaded from `nexus/registry.yaml`, fail-open on unknown ids) inside `sofi gate-check` — a violation fails the gate exactly like a skipped gate.

**Cross-project: never.** A ticket naming two `PRJ-ID`s is invalid on its face (Teaching III). Shared needs go through `shared-packages/`.

## 5. Compact form (context already shared)

```
@08-data.dat-db-engineer -> model audit entities -> Schema.sql {workhorse·high·full}
```

For chatter and squad renders only — the appended `HANDOFFS.md` block is always the full schema. First spawn of a task = full Work Order (`constitution/01-work-order.md` §3).

## 6. Worked examples

**A `done` ticket with its evidence block:**

```md
## TKT-021 · gate 4
from: bck-api-engineer
to:   bck-lead
task: POST /auth/login per frozen contract.
consumes: docs/PRJ-0001_OpenAPI.yaml §/auth/login
expected: src/backend/app/Http/Controllers/API/LoginController.php + tests/Feature/LoginTest.php
route: workhorse · medium · ultra
status: done
evidence: |
  $ php artisan test --filter=LoginTest
  PASS  Tests\Feature\LoginTest (4 passed)
  exit code: 0
  commit: 3f9ab21 — feat(auth): POST /auth/login per OpenAPI §/auth/login
```

**An escalation pair** (original flips, up-chain ticket filed — `sofi escalate PRJ-0001 TKT-034 arc-lead "contract ambiguity"`):

```md
## TKT-034 · gate 4
from: bck-lead
to:   bck-integration-engineer
task: wire the payment webhook per integration plan.
consumes: docs/PRJ-0001_Integration_Plans.md §PSP-webhooks
expected: src/backend/app/Http/Controllers/Webhooks/PspController.php + tests
route: workhorse · medium · full
status: escalated        # was: blocked

## TKT-035 · gate 4
from: bck-lead
to:   arc-lead
type: escalation
escalated_from: TKT-034
task: webhook payload shape in Integration_Plans.md §PSP-webhooks contradicts
      OpenAPI.yaml §/webhooks/psp (field `amount` int-cents vs string-decimal).
      Decision above build authority — money surface, contract is frozen (G5:
      conflict surfaced, not silently resolved).
consumes: docs/PRJ-0001_Integration_Plans.md, docs/PRJ-0001_OpenAPI.yaml
expected: arbitrated contract correction + ADR line in DECISIONS.md
route: gatekeeper · high · full
status: open
```

**A rejection** (receiver bounces a thin handoff):

```md
status: rejected   # reason: consumes names Prototype_Spec.md but gate-2 tag absent — not frozen; reject upward per Teaching II.
```

## 7. Why tickets and not chat

A ticket survives the session that wrote it (git-spined: producer checkpoints — نقطة — before `done`, receiver `sofi sync`s before `accepted`); it is grep-able (`sofi brain-query`), validate-able (fail-closed), and it carries the route so the economics stay auditable. Chat carries a status line; the bus carries the work. Big brain, small mouth. 🪨
