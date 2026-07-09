---
name: arc-integration-architect
description: "Third-party integration plans, every field verified from authoritative source."
---
# Architecture - Integration Architect

Scan webhook/event config and generate Mermaid sequence diagrams for event-driven flows. Trace external events through controllers, dispatchers, and handlers.

## Tool
`.claude/tools/arc/integration-architect/webhook-map.sh`

## When to use
- Gate 3: document integration architecture as part of package
- New webhook integration: visualize the event flow before building
- Debugging event chains: confirm listeners and handlers are wired correctly

## How to use
```bash
.claude/tools/arc/integration-architect/webhook-map.sh <PRJ-ID> [event-name]
```

## Input
- `PRJ-ID` — project with `app/Events/`, `app/Listeners/`, `routes/webhooks.php`
- `event-name` — optional filter to scope diagram to one event

## Output
- Mermaid `sequenceDiagram` with External System → Webhook Controller → Event Dispatcher → Handler
- Handlers resolved by grep-matching event class names in Listener files
- Prints `%%| diagram` render hint for markdown

## Related
- `engine/agents/arc/integration-architect.md`
- `.claude/tools/arc/integration-architect/webhook-map.sh`
