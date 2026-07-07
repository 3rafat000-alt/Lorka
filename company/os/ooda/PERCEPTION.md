# Layer 1: Perception — Perception Engine

> Converts raw signals from the environment into structured observations the agent can reason about.

## Architecture

```
External Sources          Adapters              Parser               Observation Queue
┌──────────┐         ┌─────────────┐       ┌────────────┐        ┌────────────────┐
│ Slack    │────────▶│ SlackAdapter│──────▶│            │        │                │
├──────────┤         ├─────────────┤       │   LLM      │        │ Priority Queue │
│ GitHub   │────────▶│ GitHubAdapter│──────│  Parser    │───────▶│ (reasoned)     │
├──────────┤         ├─────────────┤       │ (Claude)   │        │                │
│ Jira     │────────▶│ JiraAdapter │──────▶│            │        └────────────────┘
├──────────┤         ├─────────────┤       └────────────┘
│ APIs     │────────▶│ PollAdapter │
└──────────┘         └─────────────┘
```

## Source Adapters

### Slack Adapter
- **Events**: message, reaction_added, channel_created, member_joined
- **Filtering**: ignore bot messages, ignore own messages
- **Rate limit**: 1 msg/sec per workspace

### GitHub Adapter
- **Webhooks**: push, pull_request, issues, issue_comment, workflow_run
- **Polling**: check runs every 60s for CI status changes
- **Filter**: only watched repos (config map)

### Jira Adapter
- **Polling**: check updated issues every 120s
- **Filter**: only issues assigned to SOFI or with SOFI tag

### API Poll Adapter
- **Configurable endpoints**: health checks, metrics, custom webhooks
- **Interval**: per-endpoint config (default 300s)

### Email Adapter
- **IMAP**: read from configured inbox
- **Filter**: SOFI-tagged subjects or known senders

## Observation Schema

Every observation is normalized:

```json
{
  "id": "obs_<ulid>",
  "source": "slack|github|jira|api|email",
  "type": "message|event|alert|change",
  "timestamp": "ISO8601",
  "raw": { ... },
  "parsed": {
    "intent": "question|request|alert|update|decision",
    "summary": "LLM-generated 1-line summary",
    "urgency": 0.0–1.0,
    "entities": ["user:123", "repo:sofi", "issue:#42"],
    "requires_action": true|false,
    "suggested_tools": ["git", "search", "slack"]
  },
  "fingerprint": "sha256(dedup key)"
}
```

## Deduplication

Each observation is fingerprinted. If identical fingerprint exists in memory within TTL (default 300s), the observation is dropped. This prevents duplicate processing from webhook retries.

## Perception Loop

```python
def perceive(self) -> List[Observation]:
    observations = []
    for adapter in self.adapters:
        raw_events = adapter.poll()
        for event in raw_events:
            parsed = self.llm.parse(event)  # structured understanding
            obs = Observation(source=adapter.name, raw=event, parsed=parsed)
            if not self.is_duplicate(obs):
                observations.append(obs)
    return self.prioritize(observations)
```

## Priority Rules

| Urgency | Condition | Action |
|---------|-----------|--------|
| 1.0 | Security alert, production down | Immediate execution |
| 0.8 | User mention, CI failure | Next cycle, no delay |
| 0.5 | Normal message, PR review | Queue, normal priority |
| 0.2 | Informational, digest | Batch, process hourly |
| 0.0 | Noise, auto-reply | Drop |
