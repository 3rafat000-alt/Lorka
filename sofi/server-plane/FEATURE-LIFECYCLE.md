# SOFI Feature Lifecycle over WhatsApp (n8n conductor)

Drive a full SOFI feature — through all 9 gates, with the real agent team — from your
WhatsApp self-chat. **n8n is the maestro** (visible stages, state, approvals); the
**gateway + Claude** are the team (each gate runs a real SOFI agent that can spawn its
own sub-team). State lives in the n8n **Data Table `sofi_features`** (id
`W1t0OqToRVJ0E2oo`), so long runs are visible and resumable — no long-paused executions.

## Commands (self-chat, always prefixed `sofi ` / `صوفي `)

| Command | Does |
|---|---|
| `sofi ميزة <وصف>` | Start a feature — creates a row, dispatches Gate 0 (Inception) |
| `sofi وافق #<id>` | Approve the pending gate and continue |
| `sofi حالة #<id>` | Show a feature's gate + status + last summary |
| `sofi ألغِ #<id>` | Cancel a feature |
| `sofi مساعدة` | Show the command list |
| `sofi <anything else>` | Falls through to the two-stage smart classifier (wf10) |

## The 9 gates → agent roles

| Gate | Name | Role dispatched | Approval before? |
|---|---|---|---|
| 0 | Inception | chief-product-strategist | — (you started it) |
| 1 | Discovery | ux-researcher | auto |
| 2 | Design | ui-ux-designer | auto |
| 3 | Architecture | principal-system-architect | ✋ `sofi وافق` |
| 4 | Build | tier-2-advisor | ✋ `sofi وافق` |
| 5 | Quality | qa-sre-lead | auto |
| 6 | Staging/UAT | devops-cloud-lead | ✋ `sofi وافق` |
| 7 | Prod | devops-cloud-lead | ✋ `sofi وافق` |
| 8 | Observe | observability-sre | auto |

Non-approval gates auto-advance (each sends a WhatsApp summary as it completes).
Approval gates pause and wait for `sofi وافق #<id>` — so you keep control at the big
commitment points (architecture freeze, build, staging, prod). Change the approval set
in the `GATES` map (`approve: true/false`) inside wf20/wf21's code nodes.

## Flow

```
WhatsApp  sofi ميزة <x>
   │
   ▼  wf10 · Shortcut Router → Call Feature Engine
   ▼
wf20 · Feature Command (webhook /sofi-feature)
   ├─ start:   Data Table insert (gate 0) → build gate RCCF → gateway /dispatch (async) → Ack
   ├─ advance: Data Table get → dispatch current gate → Ack
   ├─ cancel:  Data Table update status=cancelled
   └─ status:  Data Table get → WhatsApp summary
        │  gateway runs `claude -p` as the gate's role (may spawn its own sub-team)
        ▼  on finish → POST callback
wf21 · Feature Gate Callback (webhook /sofi-feature-cb)
   ├─ update Data Table (gate = next, status, last_output)
   ├─ failed   → WhatsApp error
   ├─ complete → WhatsApp "done"  (after gate 8)
   ├─ approve  → WhatsApp "gate N needs approval: sofi وافق #id"
   └─ advance  → WhatsApp summary → POST wf20 {action:advance}  (dispatch next gate)
```

## Workflows & state

- `n8n/workflows/20-feature-command.json` — wf20 (start·advance·cancel·status + gate dispatch)
- `n8n/workflows/21-feature-callback.json` — wf21 (advance·approve·complete·failed)
- wf10's **Shortcut Router** routes `ميزة/وافق/حالة/ألغِ/مساعدة` to wf20 (else → classifier)
- Data Table **`sofi_features`**: `title, gate, status, chat_id, last_output, job_id`
  (+ built-in `id` = the feature id, `createdAt/updatedAt`). View/edit it in the n8n UI.

## Security & config notes

- All webhook auth uses `$env.SOFI_GATEWAY_TOKEN` (Code nodes + httpRequest headers) —
  it resolves at runtime, so **no literal token is stored in the workflows** (repo-safe).
  The OpenWA Trigger's `webhookSecret` is the one exception — it must be a FIXED value
  (see SETUP.md), because n8n 2.28 won't evaluate `$env` in the webhook-verify path.
- Gate model is `sonnet` by default (workhorse). Agents escalate internally if needed.
- Re-import caveat: after any API/CLI change, do NOT click Publish / revert versions in
  the n8n editor — it reverts applied changes.

## Verified

State machine proven via simulated callbacks: a gate-5 `done` callback correctly moved a
feature to `gate 6 / awaiting_approval` and stored the summary; `sofi حالة #<id>` routes
WhatsApp → wf10 → wf20 → Data Table → reply (HMAC 200, `$env` token auth). A real
`sofi ميزة <x>` runs Gates 0→1→2 automatically then pauses at Gate 3 for approval.
