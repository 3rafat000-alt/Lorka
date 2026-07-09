# 🔄 Handoff Protocol

## Before Handoff

1. `sofi checkpoint <PRJ>` — commit all work
2. Append CONTEXT.md — what was done, what was decided
3. Update STATE.md — new `head_sha`, current gate
4. Write next ticket in HANDOFFS.md — who→what→when

## After Handoff

The receiving agent:
1. `sofi sync <PRJ>` — orient
2. Read STATE.md + CONTEXT.md + HANDOFFS.md
3. Start on recorded `head_sha`

## Reject Upward

If upstream deliverables are incomplete → **do not proceed.** Write:

```
BLOCKED: Gate <N> deliverables missing/incomplete.
Required: <artifact path>
Escalated to: <room-lead>
```

## Ticket Format

```
TKT-00XX: <title>
From: <agent> → To: <agent>
Gate: <N>
Artifact: <path>
Depends on: TKT-00XX (if any)
Status: pending | active | blocked | done | escalated
```
