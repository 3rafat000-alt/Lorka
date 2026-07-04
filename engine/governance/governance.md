# 🏛️ Multi-Project Governance

## 1. Contextual Isolation
- Each project = unique **`PROJECT_ID`** (`PRJ-XXXX`).
- Memory, vector embeddings (Pinecone/ChromaDB), chat history are **partitioned by `PROJECT_ID`**.
- **Never** cross-reference code/decisions between projects unless explicitly shared via `shared-packages`.

## 2. Shared Component Library
- Central repo **`shared-packages`**.
- Any generic, reusable utility/helper/UI component **must** be refactored there and imported — never duplicated.

## 3. Resource Allocation & Prioritization
Tags: `CRITICAL · HIGH · MEDIUM · LOW`.

| Priority | Model ceiling | Effort ceiling | Behavior under contention |
|----------|:--:|:--:|------|
| CRITICAL | Opus 4.8 | max | full squads, may bump +1 tier/effort |
| HIGH | Opus 4.8 | high | accelerated |
| MEDIUM | Sonnet 4.6 | high | normal pace |
| LOW | Sonnet 4.6 | medium | **paused first**, budget reallocated to CRITICAL |

The CEO Agent may pause LOW projects and reallocate token budget + squads to CRITICAL work to hit deadlines.

## 4. Scope Control
- Any feature request outside the frozen Journey Map → **Backlog** for next quarter. Current sprint is protected.
- The Chief Product Strategist is the sole owner of scope changes.

## 5. Cross-Project Synchronization
Weekly simulated executive summary: review all active `PRJ`s, update stakeholders, re-baseline timelines around bottlenecks. Output: `Exec_Summary_[week].md`.

## 6. Auditability
Every agent turn logs its route (`model · effort · caveman`) and token estimate. The CEO reviews routes weekly to catch over-spend (e.g. Opus used where Sonnet suffices).
