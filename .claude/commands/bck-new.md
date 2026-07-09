---
description: "Build backend for new feature. /bck-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `bck-lead` — the main session *wears* this persona (`.claude/agents/bck-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 BACKEND — NEW FEATURE: $ARGUMENTS

## Delegation (parallel)

### 1. API Engineer — @bck-api-engineer
🎭 **Role:** API Engineer — endpoints
📂 **Context:** API contract frozen · Gate 4
🎯 **Command:** Implement every endpoint per OpenAPI contract. 422-JSON errors. Integration tests
📐 **Format:** Code in `app/Http/Controllers/API/` · `routes/api.php` · `tests/Feature/`

### 2. Domain Engineer — @bck-domain-engineer
🎭 **Role:** Domain Engineer — business logic
📂 **Context:** Feature + API contract
🎯 **Command:** Implement services, business logic. Money: buy≥sell invariant, fixed-precision. Guard tests per invariant
📐 **Format:** Code in `app/Services/` · `app/Models/` · `tests/Unit/`

### 3. Blade Engineer — @bck-blade-engineer
🎭 **Role:** Blade Engineer — views
📂 **Context:** UI spec frozen
🎯 **Command:** Implement Blade layouts + components. Every component: empty/loading/error/success states
📐 **Format:** Code in `resources/views/`

### 4. Queue Engineer — @bck-queue-engineer
🎭 **Role:** Queue Engineer — async tasks
📂 **Context:** Feature with async requirements
🎯 **Command:** Implement idempotent job handlers, retry/backoff/DLQ, WebSocket channels. Worker health checks
📐 **Format:** Code in `app/Jobs/` · `app/Events/` · `tests/Feature/`

### 5. Integration Engineer — @bck-integration-engineer
🎭 **Role:** Integration Engineer — third-party
📂 **Context:** Integration plan frozen
🎯 **Command:** Implement connections + webhook handlers per documented shape. Mock/test harnesses
📐 **Format:** Code in `app/Integrations/` · `tests/Feature/`

## Code Review
`@bck-code-reviewer` — adversarial diff before merges

## Handoff
→ Elif Kaya reviews + merges → QA Room `/qa-new "backend: $ARGUMENTS"`
