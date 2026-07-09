---
description: "Build data layer for new feature. /dat-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `dat-lead` — the main session *wears* this persona (`.claude/agents/dat-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 DATA — NEW FEATURE: $ARGUMENTS

## Delegation (parallel)

### 1. Database Engineer — @dat-db-engineer
🎭 **Role:** Database Engineer — migrations + queries
📂 **Context:** Data architecture frozen · Gate 3–4
🎯 **Command:** Implement reversible migrations. EXPLAIN on hot paths. Indexes. Kill N+1 queries
📐 **Format:** Migration files · `database/migrations/`

### 2. Cache Engineer — @dat-cache-engineer
🎭 **Role:** Cache Engineer — Redis layer
📂 **Context:** Feature with caching requirements
🎯 **Command:** Implement Redis caching. Stampede-safe invalidation. TTL per entry
📐 **Format:** Code in `app/Cache/` · Redis config

### 3. Analytics Engineer — @dat-analytics-engineer
🎭 **Role:** Analytics Engineer — event pipelines
📂 **Context:** Feature with analytics requirements
🎯 **Command:** Build exported event pipelines. Product metric models — each with definition, source query, expected range
📐 **Format:** Code in `app/Analytics/` · metric definitions

### 4. ML Engineer — @dat-ml-engineer
🎭 **Role:** ML Engineer — AI features
📂 **Context:** Feature with ML/AI requirements
🎯 **Command:** Integrate ML behind eval suite (accuracy/latency/cost). Failover path to deterministic rule
📐 **Format:** Code in `app/ML/` · eval suite · fallback

### 5. ETL Engineer — @dat-etl-engineer
🎭 **Role:** ETL Engineer — import/export/sync
📂 **Context:** Feature with batch data operations
🎯 **Command:** Implement idempotent resumable batch ops. Progress tracking, error reporting, audit log
📐 **Format:** Code in `app/ETL/` · batch jobs

### 6. Privacy Officer — @dat-privacy-officer
🎭 **Role:** Privacy Officer — PII classification
📂 **Context:** All data for feature $ARGUMENTS
🎯 **Command:** Classify every field as PII/non-PII/sensitive. Define retention windows. Map encryption-at-rest
📐 **Format:** `docs/Privacy_Map.md` · classification registry

## Handoff
→ Günther Weber reviews + merges → QA Room `/qa-new "data: $ARGUMENTS"`
