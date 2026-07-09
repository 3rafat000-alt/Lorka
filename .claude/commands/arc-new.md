---
description: "Architecture for new feature. /arc-new <feature>"
argument-hint: "[description]"
---
> **Lead persona:** `arc-lead` — the main session *wears* this persona (`.claude/agents/arc-lead.md`) or delegates one hop. Flat topology: parallelize with multiple spawns in one message; never nest.

# 🆕 ARCHITECTURE — NEW FEATURE: $ARGUMENTS

## Delegation

### 1. System Architect — @arc-system-architect
🎭 **Role:** System Architect — stack + components
📂 **Context:** Design frozen · Gate 3
🎯 **Command:** Produce component diagram, stack decisions, traceability map (screen→component→endpoint→data). Each ADR has rollback plan
📐 **Format:** `docs/System_Architecture.md` · Mermaid diagram · ADR log

### 2. Data Architect — @arc-data-architect
🎭 **Role:** Data Architect — schema + migrations
📂 **Context:** System architecture direction
🎯 **Command:** Produce schema DDL, ER diagram. Every migration reversible
📐 **Format:** `docs/Data_Architecture.md` · schema DDL · migration plan

### 3. API Architect — @arc-api-architect
🎭 **Role:** API Architect — contract
📂 **Context:** System architecture + feature scope
🎯 **Command:** Produce frozen API contract (OpenAPI 3.x or GraphQL SDL). Every endpoint, shape, error code. Webhook shapes + signatures
📐 **Format:** `docs/API_Contract.yaml` · backward-compatible

### 4. Integration Architect — @arc-integration-architect
🎭 **Role:** Integration Architect — third-party
📂 **Context:** Feature needs integrations
🎯 **Command:** Produce integration plan. Every field verified from authoritative source. Offline/retry/degraded design
📐 **Format:** `docs/Integration_Plan.md` · field-level citations

### 5. Infrastructure Architect — @arc-infra-architect
🎭 **Role:** Infrastructure Architect — network + scaling
📂 **Context:** Feature architecture finalized
🎯 **Command:** Design network segmentation, scaling strategy, DR posture. Cost vs reliability per decision
📐 **Format:** `docs/Infrastructure_Architecture.md`

### 6. Review Architect — @arc-review-architect
🎭 **Role:** Review Architect — 4-pillar adversarial review
📂 **Context:** All architecture artifacts
🎯 **Command:** Run 4-pillar review (system/data/API/infra) × 7 Steel Rules. Find holes. Adversarial stance
📐 **Format:** `docs/Architecture_Review.md` · SEV-priority findings · pass/revise verdict

## Handoff
→ Vikram Rao signs → CTO approves → Gateway dispatches to Build rooms `/bck-new "$ARGUMENTS"`, `/fnt-new "$ARGUMENTS"`, `/mob-new "$ARGUMENTS"`, `/dat-new "$ARGUMENTS"`
