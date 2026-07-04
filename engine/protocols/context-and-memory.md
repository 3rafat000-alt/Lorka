# 🗂️ Context & Memory — the company brain

> **Foundation:** This protocol serves Teaching **III (Radical Isolation)** — every project has its own brain, fully siloed — and Teaching **I (Design is Truth)** — the brain is the record of truth; if it isn't in `CONTEXT.md`, it isn't true. Read `engine/DOCTRINE.md` before this file.

Shared state that lets 30 agents act coherently without re-deriving. One brain per project, fully isolated.

## Location
```
projects/<PRJ-ID>/
├── _context/                ← THE BRAIN (read first, write last)
│   ├── STATE.md             current gate, active agent, status, blockers
│   ├── CONTEXT.md           durable facts: stack, constraints, key decisions
│   ├── DECISIONS.md         ADR log — one entry per irreversible choice
│   ├── HANDOFFS.md          ticket queue: who→who, what, expected output
│   └── LESSONS.md           v5: distilled procedural memory (reflection engine)
├── docs/                    blueprint, personas, journey, prototype, threat model
├── src/{backend,frontend,mobile}/
└── shared -> ../../shared-packages  (symlink; reuse, never duplicate)
```

## Read order (every agent, before acting)
`STATE.md` → your inbound ticket in `HANDOFFS.md` → `CONTEXT.md` → `DECISIONS.md` → the specific upstream artifact you consume.

## Write order (every agent, after acting)
1. Artifact → `projects/<PRJ-ID>/docs/` or `src/`.
2. New durable fact/decision → append to `CONTEXT.md` (and `DECISIONS.md` if irreversible).
3. Update `STATE.md` (advance gate / set blocker).
4. Append next ticket → `HANDOFFS.md`.

## STATE.md shape
```md
# STATE — PRJ-XXXX
gate: 3 (Technical Architecture)
active: principal-system-architect
status: in_progress | blocked | gate_signed_off
priority: HIGH
blockers: none
last_route: opus-4-8 · high · full
updated_by: <agent>
```

## DECISIONS.md (ADR) shape
```md
## ADR-007 · Postgres over Mongo
date: <from CEO, never invented>
gate: 3 · by: data-schema-engineer
why: relational integrity for audit log; journey needs joins.
consequences: no schemaless; migrations + rollback required.
```

## Isolation rules
- An agent reads/writes ONLY its own `projects/<PRJ-ID>/`.
- Cross-project reference is forbidden unless the fact lives in `shared-packages/`.
- Vector memory (Pinecone/ChromaDB) is namespaced by `PRJ-ID`. No shared namespace.

## Compression
Brain files are memory → compress with `caveman-compress` when they grow (keeps `.original.md` backup). ~46% input-token saving on every subsequent read.

## Memory types (v5 — the three-store model)
The frontier agent-memory literature (LangMem, Memp arXiv:2508.06433, the memory-evolution survey arXiv:2605.06716) converges on three memory types with different write rules. SOFI's brain already maps onto them — v5 names the mapping so the reflection engine can consolidate by type instead of re-reading raw logs:
- **Semantic** (durable facts / stack / constraints) → `CONTEXT.md`. Append-only; rarely invalidated.
- **Episodic** (records of specific tickets: who did what, what happened) → `HANDOFFS.md`. Raw episodes; retained by default, distilled on schedule (never per-turn — continuous LLM updates measurably degrade memory quality, arXiv:2605.12978).
- **Procedural** (memory that changes future *behavior*: lessons, reusable patterns, ADRs) → `DECISIONS.md` (irreversible choices) + `LESSONS.md` (distilled "what-failed → rule" lessons from the reflection engine). This is the store that should feed back into how agents act, not just be a log.
- **Working** (the live context window) is volatile — losing it is fine, losing the three persistent stores is not. `_scratch/` is working memory on disk, purged at gate exit.

## Structured frontmatter (v5 — queryable brain)
Ticket and lesson blocks may carry lightweight frontmatter so `sofi brain-query` and the reflection engine can filter without full-file reads (the append-only prose stays human-readable):
```md
## TKT-021 · gate 4
from: tier-2-advisor → to: database-engineer
type: feature            # feature | fix | audit | security | chore | refactor
mem: episodic            # semantic | episodic | procedural
status: open | done | blocked → escalated ...
```
Query: `sofi brain-query <PRJ> status=blocked type=security`. Fields are optional and additive — existing tickets without frontmatter still parse. Grep-first + frontmatter-tagged markdown is deliberately chosen over a vector DB: at SOFI's scale (tens of agents, a handful of projects) it is sufficient and matches *few token do trick* — a vector/RAG memory layer would be over-engineering (research verdict, `.claude/docs/ai-guides/research/context-engineering-memory.md`).
