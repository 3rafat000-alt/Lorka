# Protocol 02: OODA Loop — SOFI Autonomous Operating Cycle

> **Every SOFI agent thinks and acts in OODA cycles.** This protocol defines how the Observe-Orient-Decide-Act-Reflect-Learn loop integrates with the 9-gate lifecycle.

## Status: PILOT
| Stage | Date | Notes |
|-------|------|-------|
| ✦ Proposed | 2026-06-30 | Initial architecture |
| ◇ Piloting | — | First agent running OODA |
| ✓ Active | — | All agents default to OODA |

## Core Loop

SOFI agents never stop. Between ticks, between tasks, between gates — the loop runs:

```
┌─────────────────────────────────────────────────────────────────┐
│                         OODA LOOP                                │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ OBSERVE  │───▶│  ORIENT  │───▶│  DECIDE  │───▶│   ACT    │  │
│  │ perceive │    │ remember │    │  reason  │    │ execute  │  │
│  └──────────┘    └──────────┘    └──────────┘    └────┬─────┘  │
│       ▲                                                │        │
│       │            ┌──────────┐                        │        │
│       └────────────│  LEARN   │◀───────────────────────┘        │
│                    │ reflect  │                                  │
│                    └──────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Phase Details

### 1. OBSERVE (perception)
- Collect inputs from environment: file changes, git events, user messages, API responses
- Parse into structured observations with urgency rating
- Deduplicate against recent observations (fingerprint + TTL)
- **Input**: raw signals from adapters
- **Output**: prioritized `Observation[]`
- **Time**: < 2s

### 2. ORIENT (orientation)
- Load short-term context (current session state)
- Retrieve long-term memory (vector DB): past decisions, failures, patterns
- Augment observation with relevant history
- **Input**: Observation + Memory
- **Output**: Enriched context
- **Time**: < 1s

### 3. DECIDE (decision)
- Select reasoning mode:
  - **ReAct** (default): think → act → think → act (iterative)
  - **Plan-Execute**: decompose → plan → execute DAG → evaluate
  - **Reflexion**: act → reflect → improve → act again
- Choose tool(s) and parameters
- **Input**: Context
- **Output**: Plan or Decision (tool + params)
- **Time**: < 10s (LLM call)

### 4. ACT (execution)
- Execute selected tool(s) in sandboxed environment
- Log all calls to audit trail
- Handle failures gracefully (retry, escalate, or report)
- **Input**: Decision
- **Output**: Tool results
- **Time**: variable (1ms–5min)

### 5. REFLECT (reflection)
- Self-evaluate: did the action achieve the goal?
- Score: 0.0–1.0 across criteria (achievement, efficiency, correctness)
- Extract key insight and improvements
- **Input**: Cycle state (observation → result)
- **Output**: Reflection (score + insight + memory updates)
- **Time**: < 5s

### 6. LEARN (learning)
- Store reflection in long-term memory
- Apply memory updates (preferences, patterns, failures)
- Run period detection every 10 cycles
- Consolidate every 24 hours
- **Input**: Reflection
- **Output**: Memory entries
- **Time**: < 1s

## Integration with 9-Gate Lifecycle

| Gate | OODA Mode | Focus |
|------|-----------|-------|
| 0 Inception | Plan-Execute + Reflexion | Strategy, research, PRD |
| 1 Discovery | ReAct + Reflexion | UX research, journey maps |
| 2 Design | ReAct + Plan-Execute | UI/UX design iterations |
| 3 Architecture | Plan-Execute + Reflexion | System design, data flow |
| 4 Build | ReAct (default) | Development, code |
| 5 Quality | ReAct + Reflexion | Testing, bug fixing |
| 6 Staging/UAT | ReAct | Deployment, verification |
| 7 Prod | ReAct (cautious) | Production deployment |
| 8 Observe | ReAct + Pattern Detection | Monitoring, alerting |

## Agent States

```
IDLE ──▶ OBSERVING ──▶ ORIENTING ──▶ DECIDING ──▶ ACTING ──▶ REFLECTING
  ▲                                                              │
  └──────────────────────────────────────────────────────────────┘
```

- **IDLE**: Waiting for interval or event
- **OBSERVING**: Collecting inputs
- **ORIENTING**: Retrieving memory, building context
- **DECIDING**: LLM reasoning, tool selection
- **ACTING**: Tool execution
- **REFLECTING**: Self-evaluation, memory storage

## Safety & Controls

| Control | Implementation |
|---------|---------------|
| Max cycles without human | `max_cycles_without_human: 50` — then pause |
| Tool approval | High/critical tools require approval |
| Budget limits | Daily token budget, pause when exceeded |
| Sandbox | All tool execution in an isolated sandbox |
| Audit trail | Every tool call logged with trace_id |
| Kill switch | `touch /tmp/sofi-stop` stops the loop |

## Token Efficiency

| Strategy | Savings | Mechanism |
|----------|---------|-----------|
| Context Compression | ~60% | Compress memories before LLM call |
| Model Routing | ~50% cost | Haiku/Sonnet/Opus by complexity |
| Event-Driven | ~90% calls | No polling — async EventBus |
| Token Budget | prevents runaway | Economy mode at >80% daily limit |
| Noise Filter | ~90% events | Rule-based drop before LLM |
| System Prompt | ~50 tokens | Rules only, no prose |
| Session Summarization | ~50% | Load summary, not raw history |

### Model Routing Table
| Complexity | Model | Cost/M tokens | When |
|------------|-------|--------------|------|
| <0.3 | Haiku | $0.25 | Classification, reflection, summarization |
| 0.3-0.7 | Sonnet | $3.00 | Planning, coding, analysis (default) |
| >0.7 | Opus | $15.00 | Security, production, architecture decisions |

### Budget Controls
- `daily_token_limit`: 100K default (soft cap → economy mode)
- Economy mode: all LLM calls forced to Haiku, context window halved
- `check_before_call()`: returns `normal|economy|blocked`
- Budget resets daily at UTC midnight

## Configuration

See `engine/ooda/engine/config.yaml` (v2 token-efficient) for full configuration reference.
Engine entry point: `engine/ooda/engine/main.py`
