---
name: bck-integration-engineer
description: "Third-party connections, webhook handlers per documented shape."
---
# Backend - Integration Engineer

Scaffold a complete webhook handler for external providers: signature-verification middleware, event class, and webhook controller.

## Tool
`.claude/tools/bck/integration-engineer/webhook-handler.sh`

## When to use
- New third-party integration: stripe, github, slack, or any webhook provider
- Gate 4 integrations: wire up external event ingestion
- Adding webhook endpoints: generate all layers (middleware, event, controller)

## How to use
```bash
.claude/tools/bck/integration-engineer/webhook-handler.sh <PRJ-ID> <provider> <event>
```

## Input
- `PRJ-ID` — project directory
- `provider` — provider name (e.g. `stripe`, `github`, `slack`)
- `event` — event type string (e.g. `payment_intent.succeeded`, `push`)

## Output
- `app/Http/Middleware/Verify{Provider}Signature.php` — signature verification middleware
- `app/Events/{Provider}{Event}.php` — dispatchable event class with payload
- `app/Http/Controllers/Webhooks/{Provider}WebhookController.php` — invokable controller
- Route registration hint with middleware chain

## Related
- `engine/agents/bck/integration-engineer.md`
- `.claude/tools/bck/integration-engineer/webhook-handler.sh`
