# OODA Loop — SOFI Autonomous Agent Engine

> **OODA loop for the autonomous agent:** Observe → Orient → Decide → Act → Reflect → Learn

## Philosophy

SOFI operates on an infinite OODA loop — not linear task execution. Every cycle feeds the next. The agent perceives, reasons, acts, and reflects continuously. This is how SOFI becomes **autonomous**: it doesn't wait for instructions, it observes changes and decides what to do.

```
                    ┌─────────────────────────────────┐
                    │         PERCEPTION               │
                    │  (Slack · GitHub · Jira · APIs)  │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │         MEMORY (Dual)            │
                    │  Short-term (context window)     │
                    │  Long-term  (vector DB)          │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      REASONING & PLANNING        │
                    │  ReAct / Plan-Execute / Reflexion│
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │         DECISION                 │
                    │  (LLM chooses action + tool)     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │         EXECUTION (Tools)        │
                    │  Code · Search · Comm · Deploy   │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      REFLECTION (Learn)          │
                    │  What worked? What failed?       │
                    │  Store in long-term memory       │
                    └──────────────┬──────────────────┘
                                   │
                          (loop back to Perception)
```

## Layers

| Layer | File | Tech |
|-------|------|------|
| 1. Perception | `PERCEPTION.md` | Webhooks + Polling + LLM parsing |
| 2. Memory | `MEMORY.md` | ChromaDB / pgvector + Context |
| 3. Reasoning | `REASONING.md` | ReAct + Plan-Execute + Reflexion |
| 4. Tools | `TOOLS.md` | Isolated sandbox + API gateway |
| 5. Reflection | `REFLECTION.md` | Self-eval + pattern detection |
| Engine | `engine/ooda/engine/main.py` | Python OODA loop runner (core: `engine/ooda/engine/core/agent.py`) |
| Agents | `agents/*.md` | Per-agent OODA configurations |

## Principles

1. **Every action leaves a trace** — stored in vector memory for future reference
2. **Reflection is not optional** — each cycle evaluates itself before the next
3. **Failures are data** — errors become training signals, not just rollbacks
4. **Memory decays** — old context fades unless reinforced (recency-weighted retrieval)
5. **Tools are capabilities** — agent discovers what it can do via tool registry
6. **Human-in-the-loop** — critical decisions require approval; autonomy is earned

## Getting Started

```bash
# Install Python dependencies
pip install -r engine/ooda/engine/requirements.txt

# Run the OODA loop
python engine/ooda/engine/main.py --config engine/ooda/engine/config.yaml
```

See `engine/protocols/03-ooda-loop.md` for the operating protocol.
